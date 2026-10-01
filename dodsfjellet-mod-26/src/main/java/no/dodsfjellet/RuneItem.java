package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** Runer gir evner: høyreklikk for å bruke, med nedkjøling. */
public class RuneItem extends Item {
    public enum Evne {
        SKYGGESPRANG("skyggesprang", "Skyggesprang", "Kast deg fremover og bli usynlig et øyeblikk", 80),
        SJELESKJOLD("sjeleskjold", "Sjeleskjold", "Åtte ekstra hjerter og motstand i 10 sekunder", 500),
        DODSNOVA("dodsnova", "Dødsnova", "Sjeleeksplosjon som skader og visner alt rundt deg", 300),
        BLODHOST("blodhost", "Blodhøst", "I 10 sekunder heler slagene dine deg", 600),
        ANDESPRANG("andesprang", "Åndesprang", "Hopp høyt og sveve sakte ned", 160),
        VOKTERKALL("vokterkall", "Vokterkall", "Kall to Åndevakter som kjemper for deg i 30 sekunder", 1200);

        public final String navn;
        public final String visning;
        public final String beskrivelse;
        public final int nedkjoling;

        Evne(String navn, String visning, String beskrivelse, int nedkjoling) {
            this.navn = navn;
            this.visning = visning;
            this.beskrivelse = beskrivelse;
            this.nedkjoling = nedkjoling;
        }
    }

    private final Evne evne;

    public RuneItem(Item.Properties props, Evne evne) {
        super(props);
        this.evne = evne;
    }

    @Override
    public InteractionResult use(Level level, Player spiller, InteractionHand hand) {
        ItemStack stack = spiller.getItemInHand(hand);
        if (spiller.getCooldowns().isOnCooldown(stack)) return InteractionResult.FAIL;
        if (level instanceof ServerLevel sl && spiller instanceof ServerPlayer sp) {
            bruk(sl, sp);
            spiller.getCooldowns().addCooldown(stack, this.evne.nedkjoling);
        }
        return InteractionResult.SUCCESS;
    }

    private void bruk(ServerLevel sl, ServerPlayer p) {
        switch (this.evne) {
            case SKYGGESPRANG -> {
                Vec3 blikk = p.getLookAngle();
                p.setDeltaMovement(blikk.x * 2.2, Math.max(0.25, blikk.y * 0.8 + 0.25), blikk.z * 2.2);
                p.connection.send(new ClientboundSetEntityMotionPacket(p));
                p.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 50, 0, false, false));
                p.fallDistance = 0;
                sl.sendParticles(ParticleTypes.LARGE_SMOKE, p.getX(), p.getY() + 1, p.getZ(), 30, 0.4, 0.6, 0.4, 0.02);
                lyd(sl, p, SoundEvents.ENDERMAN_TELEPORT, 0.7f);
            }
            case SJELESKJOLD -> {
                p.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 200, 3));
                p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 100, 1));
                sl.sendParticles(ParticleTypes.SOUL, p.getX(), p.getY() + 1, p.getZ(), 40, 0.6, 0.8, 0.6, 0.03);
                lyd(sl, p, SoundEvents.BEACON_POWER_SELECT, 1.2f);
            }
            case DODSNOVA -> {
                for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(6.0))) {
                    if (e == p || !e.isAlive() || (e instanceof VaktEntity v && v.erAlliert())) continue;
                    e.hurtServer(sl, sl.damageSources().indirectMagic(p, p), 8.0f);
                    e.addEffect(new MobEffectInstance(MobEffects.WITHER, 100, 1));
                    Vec3 r = e.position().subtract(p.position()).normalize();
                    e.push(r.x * 1.2, 0.5, r.z * 1.2);
                }
                for (int i = 0; i < 48; i++) {
                    double a = i / 48.0 * Math.PI * 2;
                    sl.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, p.getX() + Math.cos(a) * 5, p.getY() + 0.3,
                            p.getZ() + Math.sin(a) * 5, 2, 0.1, 0.1, 0.1, 0.01);
                }
                sl.sendParticles(ParticleTypes.SONIC_BOOM, p.getX(), p.getY() + 1, p.getZ(), 1, 0, 0, 0, 0);
                lyd(sl, p, SoundEvents.WARDEN_SONIC_BOOM, 1.0f);
            }
            case BLODHOST -> {
                p.addEffect(new MobEffectInstance(ModGjenstander.BLODHOST, 200, 0));
                sl.sendParticles(ParticleTypes.DAMAGE_INDICATOR, p.getX(), p.getY() + 1, p.getZ(), 20, 0.5, 0.6, 0.5, 0.1);
                lyd(sl, p, SoundEvents.WITHER_SHOOT, 0.6f);
            }
            case ANDESPRANG -> {
                Vec3 blikk = p.getLookAngle();
                p.setDeltaMovement(blikk.x * 0.6, 1.6, blikk.z * 0.6);
                p.connection.send(new ClientboundSetEntityMotionPacket(p));
                p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 140, 0));
                sl.sendParticles(ParticleTypes.CLOUD, p.getX(), p.getY(), p.getZ(), 25, 0.5, 0.1, 0.5, 0.05);
                lyd(sl, p, SoundEvents.BREEZE_JUMP, 1.0f);
            }
            case VOKTERKALL -> {
                for (int i = 0; i < 2; i++) {
                    VaktEntity v = ModEntiteter.VAKT.create(sl, EntitySpawnReason.MOB_SUMMONED);
                    if (v == null) continue;
                    double vinkel = p.getYRot() * Math.PI / 180 + (i == 0 ? 1.2 : -1.2);
                    v.snapTo(p.getX() - Math.sin(vinkel) * 2, p.getY(), p.getZ() + Math.cos(vinkel) * 2, p.getYRot(), 0);
                    v.gjorAlliert(p, 600);
                    sl.addFreshEntity(v);
                    sl.sendParticles(ParticleTypes.SOUL, v.getX(), v.getY() + 1, v.getZ(), 25, 0.3, 0.8, 0.3, 0.03);
                }
                lyd(sl, p, SoundEvents.EVOKER_CAST_SPELL, 0.8f);
            }
        }
    }

    private static void lyd(ServerLevel sl, Player p, SoundEvent lyd, float tone) {
        sl.playSound(null, p.blockPosition(), lyd, SoundSource.PLAYERS, 1.0f, tone);
    }

    @Override
    @SuppressWarnings("deprecation")
    public void appendHoverText(ItemStack s, Item.TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
        ut.accept(Component.literal("Evne: " + this.evne.visning).withStyle(ChatFormatting.LIGHT_PURPLE));
        ut.accept(Component.literal(this.evne.beskrivelse).withStyle(ChatFormatting.GRAY));
        ut.accept(Component.literal("Høyreklikk – nedkjøling " + (this.evne.nedkjoling / 20) + " s").withStyle(ChatFormatting.DARK_GRAY));
    }
}
