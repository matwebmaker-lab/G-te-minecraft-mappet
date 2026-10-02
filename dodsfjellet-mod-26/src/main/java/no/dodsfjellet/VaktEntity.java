package no.dodsfjellet;

import net.minecraft.core.UUIDUtil;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundAnimatePacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RangedBowAttackGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.RangedAttackMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.entity.projectile.arrow.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.UUID;

/**
 * Vakt som ser ut og oppfører seg som en spiller: spillernavn, spiller-skin, sprint, hopp-krit,
 * strafing, bytter til bue på avstand, spiser gulleple, skriver i chatten.
 * Med en eier (Vokterkall-runen) blir den en alliert "Åndevakt" som jakter monstre i stedet.
 */
public class VaktEntity extends Monster implements RangedAttackMob {
    private static final String[] NAVN = {
            "Glade_Ola", "Kari_Bygger", "EnderJonas", "Sol_Sigrid", "BlokkMester", "DiamondDidrik",
            "Venne_Vilde", "Emma_Builds", "Nordlys_Nils", "Hjelpsomme_Henrik", "IngridIsTheBest", "Fjellvandrer",
            "Kristian2012", "Gode_Gunnar", "Ninja_Nora", "MLG_Magnus", "Bueskytter_Bjorn", "Lys_Lukas",
            "Skattejeger", "Viking_Vilde", "Snille_Sara", "Josef_Bygger", "Modige_Daniel", "Ester_Sterk"};
    private static final String[] HEI = {"Hei! Klar for en vennlig kamp?", "Lykke til!", "Jeg vokter skatten – vis hva du kan!",
            "God dag, vandrer!", "Fred være med deg!", "Du er modig som David!", "Kom igjen, vi tar det med et smil!",
            "Skal vi se hvem som vinner?", "Velkommen! Dette blir gøy!", "Ha en velsignet dag!"};
    private static final String[] DREPT = {"gg! Godt forsøkt!", "Du klarer det neste gang!", "Reis deg igjen – du er sterkere enn du tror!",
            "Bra kjempet!", "Aldri gi opp!", "gg, prøv igjen!"};
    private static final String[] DOD = {"gg, du var flink!", "Godt spilt!", "Du vant – gratulerer!", "Wow, imponerende!",
            "Velsignet seier til deg!", "Neste gang tar jeg deg! :)"};
    private static final String[] SPISER = {"Matpause!", "Nam nam, eple!", "Takk for maten!"};

    private final RangedBowAttackGoal<VaktEntity> bueMaal = new RangedBowAttackGoal<>(this, 1.0, 20, 15.0f);
    private final MeleeAttackGoal naerMaal = new MeleeAttackGoal(this, 1.25, true);

    private boolean utstyrt;
    private int epler = 2;
    private int spiseNedtelling;
    private int byttNedtelling;
    private boolean spiser;
    private ItemStack lagretVaapen = ItemStack.EMPTY;
    private @Nullable UUID eier;
    private int levetid = -1;

    public VaktEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 10;
        this.setPersistenceRequired();
        this.byttVaapenMaal();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20.0)
                .add(Attributes.MOVEMENT_SPEED, 0.3)
                .add(Attributes.ATTACK_DAMAGE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 40.0);
    }

    public boolean erAlliert() {
        return this.eier != null;
    }

    /** Gjør vakten til en alliert Åndevakt for en spiller i et gitt antall ticks. */
    public void gjorAlliert(Player spiller, int ticks) {
        this.eier = spiller.getUUID();
        this.levetid = ticks;
        this.setCustomName(Component.literal("Åndevakt (" + spiller.getName().getString() + ")"));
        this.setCustomNameVisible(true);
        this.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.GLOWING, ticks, 0, false, false));
        this.utstyrt = false;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 16.0f));
        this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true,
                (maal, nivaa) -> !this.erAlliert()));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, Monster.class, true,
                (maal, nivaa) -> this.erAlliert() && !(maal instanceof VaktEntity v && v.erAlliert())));
    }

    private void byttVaapenMaal() {
        if (this.level() == null || this.level().isClientSide() || this.naerMaal == null || this.bueMaal == null) return;
        this.goalSelector.removeGoal(this.naerMaal);
        this.goalSelector.removeGoal(this.bueMaal);
        if (this.spiser) return;
        this.goalSelector.addGoal(4, this.getMainHandItem().is(Items.BOW) ? this.bueMaal : this.naerMaal);
    }

    @Override
    public void setItemSlot(EquipmentSlot slot, ItemStack stack) {
        super.setItemSlot(slot, stack);
        if (slot == EquipmentSlot.MAINHAND && this.level() != null && !this.level().isClientSide()) {
            this.byttVaapenMaal();
        }
    }

    @Override
    public void setTarget(@Nullable LivingEntity target) {
        if (this.erAlliert() && (target instanceof Player || (target instanceof VaktEntity v && v.erAlliert()))) {
            target = null;   // allierte angriper aldri spillere eller hverandre
        }
        LivingEntity foer = this.getTarget();
        super.setTarget(target);
        if (target instanceof Player && foer == null && !this.level().isClientSide() && this.random.nextInt(3) == 0) {
            chat(velg(HEI));
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (this.level() instanceof ServerLevel sl) {
            if (!this.utstyrt) utstyr();
            if (this.levetid > 0 && --this.levetid == 0) {
                sl.sendParticles(ParticleTypes.SOUL, this.getX(), this.getY() + 1, this.getZ(), 20, 0.3, 0.6, 0.3, 0.02);
                this.discard();
            }
        }
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        if (this.spiseNedtelling > 0) this.spiseNedtelling--;
        if (this.byttNedtelling > 0) this.byttNedtelling--;

        if (this.spiser) {
            if (!this.isUsingItem()) {
                this.spiser = false;
                this.setItemSlot(EquipmentSlot.MAINHAND, hentVaapen());
            }
            return;
        }
        LivingEntity maal = this.getTarget();
        if (maal == null || !maal.isAlive()) {
            this.setSprinting(false);
            return;
        }
        if (this.getHealth() < this.getMaxHealth() * 0.35f && this.epler > 0 && this.spiseNedtelling == 0) {
            begynnAaSpise(maal);
            return;
        }
        double avstand = this.distanceToSqr(maal);
        boolean bue = this.getMainHandItem().is(Items.BOW);
        if (this.byttNedtelling == 0) {
            if (!bue && avstand > 81 && this.hasLineOfSight(maal)) {
                this.lagretVaapen = this.getMainHandItem().copy();
                this.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.BOW));
                this.byttNedtelling = 40;
                bue = true;
            } else if (bue && avstand < 36) {
                this.setItemSlot(EquipmentSlot.MAINHAND, hentVaapen());
                this.byttNedtelling = 40;
                bue = false;
            }
        }
        this.setSprinting(!bue && avstand > 9);
        if (!bue && avstand < 12 && this.onGround() && this.random.nextInt(7) == 0) {
            this.jumpFromGround();
        }
        if (!bue && avstand < 16 && this.onGround() && this.random.nextInt(18) == 0) {
            Vec3 mot = maal.position().subtract(this.position()).normalize();
            Vec3 side = new Vec3(-mot.z, 0, mot.x).scale(this.random.nextBoolean() ? 0.35 : -0.35);
            this.setDeltaMovement(this.getDeltaMovement().add(side));
        }
    }

    private ItemStack hentVaapen() {
        ItemStack v = this.lagretVaapen.isEmpty() ? new ItemStack(Items.IRON_SWORD) : this.lagretVaapen;
        this.lagretVaapen = ItemStack.EMPTY;
        return v;
    }

    private void begynnAaSpise(LivingEntity maal) {
        ItemStack naa = this.getMainHandItem().copy();
        if (!naa.is(Items.GOLDEN_APPLE) && !naa.is(Items.BOW)) this.lagretVaapen = naa;
        this.spiser = true;
        this.epler--;
        this.spiseNedtelling = 240;
        this.setSprinting(false);
        this.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.GOLDEN_APPLE));
        this.startUsingItem(InteractionHand.MAIN_HAND);
        Vec3 bort = this.position().subtract(maal.position()).normalize().scale(6).add(this.position());
        this.getNavigation().moveTo(bort.x, bort.y, bort.z, 1.1);
        if (this.random.nextInt(3) == 0) chat(velg(SPISER));
    }

    private void utstyr() {
        this.utstyrt = true;
        if (!this.hasCustomName()) this.setCustomName(Component.literal(velg(NAVN)));
        this.setCustomNameVisible(true);
        if (this.getMainHandItem().isEmpty()) {
            this.setItemSlot(EquipmentSlot.MAINHAND,
                    new ItemStack(this.random.nextInt(3) == 0 ? Items.DIAMOND_SWORD : Items.IRON_SWORD));
        }
        boolean diamant = this.random.nextInt(3) == 0;
        for (EquipmentSlot s : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
            if (this.getItemBySlot(s).isEmpty() && this.random.nextInt(5) != 0) {
                this.setItemSlot(s, new ItemStack(rustning(s, diamant)));
            }
        }
        for (EquipmentSlot s : EquipmentSlot.values()) this.setDropChance(s, 0.0f);
    }

    private static Item rustning(EquipmentSlot s, boolean diamant) {
        return switch (s) {
            case HEAD -> diamant ? Items.DIAMOND_HELMET : Items.IRON_HELMET;
            case CHEST -> diamant ? Items.DIAMOND_CHESTPLATE : Items.IRON_CHESTPLATE;
            case LEGS -> diamant ? Items.DIAMOND_LEGGINGS : Items.IRON_LEGGINGS;
            default -> diamant ? Items.DIAMOND_BOOTS : Items.IRON_BOOTS;
        };
    }

    @Override
    public void performRangedAttack(LivingEntity target, float kraft) {
        ItemStack bue = this.getItemInHand(ProjectileUtil.getWeaponHoldingHand(this, Items.BOW));
        ItemStack prosjektil = this.getProjectile(bue);
        AbstractArrow pil = ProjectileUtil.getMobArrow(this, prosjektil, kraft, bue);
        pil.pickup = AbstractArrow.Pickup.DISALLOWED;
        double dx = target.getX() - this.getX();
        double dy = target.getY(0.3333) - pil.getY();
        double dz = target.getZ() - this.getZ();
        double h = Math.sqrt(dx * dx + dz * dz);
        if (this.level() instanceof ServerLevel sl) {
            Projectile.spawnProjectileUsingShoot(pil, sl, prosjektil, dx, dy + h * 0.2, dz, 1.8f,
                    10 - sl.getDifficulty().getId() * 3);
        }
        this.playSound(SoundEvents.ARROW_SHOOT, 1.0f, 1.0f / (this.getRandom().nextFloat() * 0.4f + 0.8f));
    }

    @Override
    public boolean doHurtTarget(ServerLevel level, Entity target) {
        boolean kritisk = !this.onGround() && this.fallDistance > 0.0;
        boolean traff = super.doHurtTarget(level, target);
        if (traff && kritisk && target instanceof LivingEntity levende) {
            levende.setInvulnerableTime(0);
            levende.hurtServer(level, this.damageSources().mobAttack(this), 3.0f);
            level.getChunkSource().sendToTrackingPlayers(this, new ClientboundAnimatePacket(target, ClientboundAnimatePacket.CRITICAL_HIT));
            this.playSound(SoundEvents.PLAYER_ATTACK_CRIT, 1.0f, 1.0f);
        }
        return traff;
    }

    @Override
    public boolean killedEntity(ServerLevel level, LivingEntity offer, DamageSource kilde) {
        if (offer instanceof Player && !this.erAlliert()) chat(velg(DREPT));
        return super.killedEntity(level, offer, kilde);
    }

    @Override
    public void die(DamageSource kilde) {
        // Bare "gg"/"lag!!" når en spiller var med i kampen – ikke når de faller i lava alene
        boolean spillerKamp = kilde.getEntity() instanceof Player || this.getTarget() instanceof Player;
        if (!this.level().isClientSide() && !this.erAlliert() && spillerKamp && this.random.nextInt(2) == 0) chat(velg(DOD));
        super.die(kilde);
    }

    private void chat(String melding) {
        if (this.level() instanceof ServerLevel sl) {
            sl.getServer().getPlayerList().broadcastSystemMessage(
                    Component.literal("<" + this.getName().getString() + "> " + melding), false);
        }
    }

    private String velg(String[] liste) {
        return liste[this.random.nextInt(liste.length)];
    }

    @Override
    protected @Nullable SoundEvent getHurtSound(DamageSource kilde) {
        return SoundEvents.PLAYER_HURT;
    }

    @Override
    protected @Nullable SoundEvent getDeathSound() {
        return SoundEvents.PLAYER_DEATH;
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput ut) {
        super.addAdditionalSaveData(ut);
        ut.putBoolean("Utstyrt", this.utstyrt);
        ut.putInt("Epler", this.epler);
        ut.putInt("Levetid", this.levetid);
        if (!this.lagretVaapen.isEmpty()) ut.store("LagretVaapen", ItemStack.CODEC, this.lagretVaapen);
        if (this.eier != null) ut.store("Eier", UUIDUtil.CODEC, this.eier);
    }

    @Override
    protected void readAdditionalSaveData(ValueInput inn) {
        super.readAdditionalSaveData(inn);
        this.utstyrt = inn.getBooleanOr("Utstyrt", false);
        this.epler = inn.getIntOr("Epler", 2);
        this.levetid = inn.getIntOr("Levetid", -1);
        this.lagretVaapen = inn.read("LagretVaapen", ItemStack.CODEC).orElse(ItemStack.EMPTY);
        this.eier = inn.read("Eier", UUIDUtil.CODEC).orElse(null);
        this.byttVaapenMaal();
    }
}
