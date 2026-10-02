package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUseAnimation;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * Gevær: øyeblikkelig treff langs siktelinjen (hitscan), magasin som må lades om med kuler fra inventaret,
 * rekyl, munningsflamme, sporlys og treffeffekter. Høyreklikk skyter, snik + høyreklikk lader om.
 * Automatgeværet skyter så lenge du holder inne. Oppgraderingssmia gir mer skade, større magasin og raskere omlading.
 */
public class GevaerItem extends Item {
    public static final ResourceKey<DamageType> SKUDD = ResourceKey.create(Registries.DAMAGE_TYPE, Reg.id("skudd"));

    /** Egenskapene til ett gevær. */
    public record Spec(String navn, float skade, int hagl, int magasin, int nedkjoling, int omlading, float spredning,
                       double rekkevidde, boolean automatisk, float rekyl, float tilbakeslag,
                       Supplier<Item> ammo, Supplier<SoundEvent> lyd, Supplier<SoundEvent> omladLyd) {}

    private final Spec spec;

    public GevaerItem(Properties props, Spec spec) {
        super(props.component(ModGjenstander.MAGASIN, spec.magasin()));
        this.spec = spec;
    }

    public Spec spec() {
        return spec;
    }

    // ------------------------------------------------------------ verdier som øker med oppgraderingsnivået
    public int magasin(ItemStack s) {
        return spec.magasin() + Math.round(spec.magasin() * 0.06f * OppgraderingssmieBlock.nivaa(s));
    }

    float skade(ItemStack s) {
        return spec.skade() * (1 + 0.09f * OppgraderingssmieBlock.nivaa(s));
    }

    int omladingTid(ItemStack s) {
        return Math.max(8, Math.round(spec.omlading() * (1 - 0.045f * OppgraderingssmieBlock.nivaa(s))));
    }

    float spredning(ItemStack s, Player p) {
        float sp = spec.spredning() * (1 - 0.05f * OppgraderingssmieBlock.nivaa(s));
        if (p.isCrouching()) sp *= 0.5f;                                   // stødigere når du sniker
        if (!p.onGround()) sp = sp * 2.0f + 1.5f;                          // mye verre i lufta
        return sp;
    }

    public static int kuler(ItemStack s) {
        return s.getOrDefault(ModGjenstander.MAGASIN, 0);
    }

    // ------------------------------------------------------------ bruk
    @Override
    public InteractionResult use(Level level, Player p, InteractionHand hand) {
        ItemStack s = p.getItemInHand(hand);
        if (p.getCooldowns().isOnCooldown(s)) return InteractionResult.FAIL;
        if (p.isShiftKeyDown() && kuler(s) < magasin(s)) {
            if (level instanceof ServerLevel sl) omlad(sl, p, s);
            return InteractionResult.CONSUME;
        }
        skyt(level, p, s);
        if (p.getCooldowns().isOnCooldown(s)) return InteractionResult.CONSUME;   // omladingen startet
        if (spec.automatisk()) {
            p.startUsingItem(hand);
        } else {
            p.getCooldowns().addCooldown(s, spec.nedkjoling());
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public void onUseTick(Level level, LivingEntity bruker, ItemStack s, int igjen) {
        if (!spec.automatisk() || !(bruker instanceof Player p)) return;
        int brukt = getUseDuration(s, bruker) - igjen;
        if (brukt > 0 && brukt % spec.nedkjoling() == 0) {
            if (p.getCooldowns().isOnCooldown(s)) {
                p.stopUsingItem();
                return;
            }
            skyt(level, p, s);
        }
    }

    @Override
    public boolean releaseUsing(ItemStack s, Level level, LivingEntity bruker, int igjen) {
        if (bruker instanceof Player p && !p.getCooldowns().isOnCooldown(s)) p.getCooldowns().addCooldown(s, spec.nedkjoling());
        return true;
    }

    @Override
    public int getUseDuration(ItemStack s, LivingEntity bruker) {
        return spec.automatisk() ? 72000 : 0;
    }

    @Override
    public ItemUseAnimation getUseAnimation(ItemStack s) {
        return ItemUseAnimation.NONE;
    }

    @Override
    public boolean isBarVisible(ItemStack s) {
        return true;
    }

    @Override
    public int getBarWidth(ItemStack s) {
        return Math.round(13.0f * kuler(s) / Math.max(1, magasin(s)));
    }

    @Override
    public int getBarColor(ItemStack s) {
        float f = (float) kuler(s) / Math.max(1, magasin(s));
        return f > 0.34f ? 0xE8C25A : 0xD23B2B;
    }

    // ------------------------------------------------------------ skyting
    private void skyt(Level level, Player p, ItemStack s) {
        if (kuler(s) <= 0) {
            if (level instanceof ServerLevel sl) {
                sl.playSound(null, p.getX(), p.getY(), p.getZ(), ModLyder.TOM, SoundSource.PLAYERS, 0.8f, 1.0f);
                if (!omlad(sl, p, s)) p.stopUsingItem();
            }
            return;
        }
        RandomSource r = p.getRandom();
        if (level.isClientSide()) {
            // rekyl: løpet sparker opp og litt til siden (bare for spilleren som skyter)
            p.setXRot(p.getXRot() - spec.rekyl() * (0.7f + r.nextFloat() * 0.5f));
            p.setYRot(p.getYRot() + (r.nextFloat() - 0.5f) * spec.rekyl() * 0.6f);
            return;
        }
        ServerLevel sl = (ServerLevel) level;
        s.set(ModGjenstander.MAGASIN, kuler(s) - 1);

        Vec3 oye = p.getEyePosition();
        Vec3 blikk = p.getLookAngle();
        Vec3 hoyre = blikk.cross(new Vec3(0, 1, 0)).normalize();
        Vec3 munning = oye.add(blikk.scale(1.1)).add(hoyre.scale(0.28)).add(0, -0.18, 0);
        float sp = spredning(s, p);
        for (int i = 0; i < Math.max(1, spec.hagl()); i++) {
            treff(sl, p, s, oye, munning, spre(blikk, sp, r));
        }

        sl.playSound(null, p.getX(), p.getY(), p.getZ(), spec.lyd().get(), SoundSource.PLAYERS,
                spec.navn().equals("snikskyttergevaer") ? 6.0f : 4.0f, 0.94f + r.nextFloat() * 0.12f);
        sl.sendParticles(new DustParticleOptions(0xFFE9B0, 0.5f), true, false, munning.x, munning.y, munning.z, 2, 0.02, 0.02, 0.02, 0);
        sl.sendParticles(ParticleTypes.SMALL_FLAME, true, false, munning.x, munning.y, munning.z, 1, 0.01, 0.01, 0.01, 0.005);
        sl.sendParticles(ParticleTypes.SMOKE, munning.x, munning.y, munning.z, 2, 0.03, 0.03, 0.03, 0.005);
        if (spec.tilbakeslag() > 0) {
            p.push(blikk.scale(-spec.tilbakeslag()));
            if (p instanceof ServerPlayer spiller) spiller.connection.send(new ClientboundSetEntityMotionPacket(spiller));
        }
        if (kuler(s) == 0 && p instanceof ServerPlayer) omlad(sl, p, s);   // tomt: lad om automatisk
        p.awardStat(net.minecraft.stats.Stats.ITEM_USED.get(this));
    }

    private static Vec3 spre(Vec3 d, float grader, RandomSource r) {
        if (grader <= 0) return d;
        double a = Math.toRadians(grader) * 0.5;
        return d.add(r.nextGaussian() * a, r.nextGaussian() * a, r.nextGaussian() * a).normalize();
    }

    private void treff(ServerLevel sl, Player p, ItemStack s, Vec3 start, Vec3 munning, Vec3 retning) {
        Vec3 slutt = start.add(retning.scale(spec.rekkevidde()));
        BlockHitResult blokk = sl.clip(new ClipContext(start, slutt, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
        if (blokk.getType() != HitResult.Type.MISS) slutt = blokk.getLocation();
        EntityHitResult mal = ProjectileUtil.getEntityHitResult(sl, p, start, slutt, new AABB(start, slutt).inflate(1.0),
                e -> e.isPickable() && !e.isSpectator() && e.isAlive() && e != p && !p.isPassengerOfSameVehicle(e), 0.15f);
        Vec3 punkt = mal != null ? mal.getLocation() : slutt;
        spor(sl, munning, punkt);

        if (mal != null) {
            Entity e = mal.getEntity();
            float dmg = skade(s);
            double fall = start.distanceTo(punkt) / spec.rekkevidde();         // haglet mister kraft på avstand
            if (spec.hagl() > 1) dmg *= (float) Mth.clamp(1.2 - fall * 1.1, 0.25, 1.0);
            boolean hode = e instanceof LivingEntity le && punkt.y >= le.getEyeY() - 0.22;
            if (hode) dmg *= 1.6f;
            Holder<DamageType> type = sl.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(SKUDD);
            DamageSource kilde = new DamageSource(type, p, p);
            e.setInvulnerableTime(0);
            if (e.hurtServer(sl, kilde, dmg)) {
                if (e instanceof LivingEntity le) le.knockback(Math.min(0.6, 0.1 + 0.015 * spec.skade()), -retning.x, -retning.z, kilde, dmg);
                sl.sendParticles(ParticleTypes.DAMAGE_INDICATOR, punkt.x, punkt.y, punkt.z, 2, 0.1, 0.1, 0.1, 0.1);
                if (p instanceof ServerPlayer sp) {
                    SoundEvent ding = hode ? SoundEvents.ARROW_HIT_PLAYER : SoundEvents.ARROW_HIT;     // treffmarkør, bare for skytteren
                    sp.connection.send(new ClientboundSoundPacket(BuiltInRegistries.SOUND_EVENT.wrapAsHolder(ding), SoundSource.PLAYERS,
                            sp.getX(), sp.getY(), sp.getZ(), 0.5f, hode ? 1.8f : 1.3f, sl.getRandom().nextLong()));
                    if (hode) sp.sendOverlayMessage(Component.literal("✦ Hodeskudd!").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
                }
            }
        } else if (blokk.getType() == HitResult.Type.BLOCK) {
            BlockState bs = sl.getBlockState(blokk.getBlockPos());
            Vec3 h = blokk.getLocation();
            sl.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, bs), h.x, h.y, h.z, 8, 0.06, 0.06, 0.06, 0.15);
            sl.sendParticles(ParticleTypes.SMOKE, h.x, h.y, h.z, 2, 0.02, 0.02, 0.02, 0.01);
            sl.playSound(null, h.x, h.y, h.z, bs.getSoundType().getHitSound(), SoundSource.BLOCKS, 0.6f, 1.4f);
        }
    }

    /** Sporlys fra munningen til treffpunktet. */
    private static void spor(ServerLevel sl, Vec3 fra, Vec3 til) {
        Vec3 d = til.subtract(fra);
        double len = d.length();
        Vec3 steg = d.normalize();
        DustParticleOptions lys = new DustParticleOptions(0xFFE7A0, 0.45f);
        for (double t = 1.0; t < len; t += 0.9) {
            Vec3 q = fra.add(steg.scale(t));
            sl.sendParticles(lys, true, false, q.x, q.y, q.z, 1, 0, 0, 0, 0);
        }
    }

    // ------------------------------------------------------------ omlading
    /** Fyller magasinet med kuler fra inventaret. Mens nedkjølingen går kan du ikke skyte. */
    boolean omlad(ServerLevel sl, Player p, ItemStack s) {
        int maks = magasin(s), har = kuler(s);
        if (har >= maks || p.getCooldowns().isOnCooldown(s)) return false;
        int trengs = maks - har;
        int fikk = p.getAbilities().instabuild ? trengs : taAmmo(p, spec.ammo().get(), trengs);
        if (fikk <= 0) {
            if (p instanceof ServerPlayer sp) {
                sp.sendOverlayMessage(Component.literal("Tom for " + Component.translatable(spec.ammo().get().getDescriptionId()).getString()
                        .toLowerCase() + "!").withStyle(ChatFormatting.RED));
            }
            return false;
        }
        s.set(ModGjenstander.MAGASIN, har + fikk);
        p.getCooldowns().addCooldown(s, omladingTid(s));
        p.stopUsingItem();
        sl.playSound(null, p.getX(), p.getY(), p.getZ(), spec.omladLyd().get(), SoundSource.PLAYERS, 1.0f, 1.0f);
        if (p instanceof ServerPlayer sp) {
            sp.sendOverlayMessage(Component.literal("Lader om... (" + (har + fikk) + "/" + maks + ")").withStyle(ChatFormatting.GRAY));
        }
        return true;
    }

    private static int taAmmo(Player p, Item ammo, int trengs) {
        int fikk = 0;
        var inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize() && fikk < trengs; i++) {
            ItemStack st = inv.getItem(i);
            if (st.is(ammo)) {
                int ta = Math.min(trengs - fikk, st.getCount());
                st.shrink(ta);
                fikk += ta;
            }
        }
        return fikk;
    }

    // ------------------------------------------------------------ verktøytips
    @Override
    @SuppressWarnings("deprecation")
    public void appendHoverText(ItemStack s, TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
        ut.accept(Component.literal("Magasin: " + kuler(s) + "/" + magasin(s)).withStyle(ChatFormatting.YELLOW));
        String skade = spec.hagl() > 1 ? String.format("%d × %.1f", spec.hagl(), skade(s)) : String.format("%.1f", skade(s));
        ut.accept(Component.literal("Skade: " + skade + "   Rekkevidde: " + (int) spec.rekkevidde()).withStyle(ChatFormatting.GRAY));
        ut.accept(Component.literal("Ammunisjon: ").withStyle(ChatFormatting.GRAY)
                .append(Component.translatable(spec.ammo().get().getDescriptionId()).withStyle(ChatFormatting.WHITE)));
        ut.accept(Component.literal(spec.automatisk() ? "Hold inne høyreklikk for å skyte" : "Høyreklikk for å skyte")
                .withStyle(ChatFormatting.DARK_GRAY));
        ut.accept(Component.literal("Snik + høyreklikk for å lade om").withStyle(ChatFormatting.DARK_GRAY));
    }
}
