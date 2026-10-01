package no.dodsfjellet;

import net.minecraft.nbt.CompoundTag;
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
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

/**
 * En vakt som ser ut og oppfører seg som en spiller: spillernavn over hodet, spiller-skin,
 * sprinter, hopper for kritiske treff, strafer, bytter til bue på avstand, spiser gulleple
 * når livet er lavt og skriver i chatten.
 */
public class VaktEntity extends Monster implements RangedAttackMob {
    private static final String[] NAVN = {
            "xX_Slayer_Xx", "PvP_Ola", "NoobKiller99", "Kari_Gamer", "EnderJonas", "SweatyTryhard",
            "BlokkMester", "DiamondDidrik", "Sigurd_PvP", "Emma_Builds", "CreeperKongen", "Nordlys_Nils",
            "TryhardTobias", "IngridIsTheBest", "LagMasterX", "Fjellulven", "Kristian2012", "GG_Gunnar",
            "Ninja_Nora", "MLG_Magnus", "Bueskytter_Bjorn", "ThorHammer07", "SkattJeger", "Viking_Vilde"};
    private static final String[] HEI = {
            "lol en til", "kom igjen da", "1v1 meg", "du er ferdig", "jeg ser deg :)", "hehe",
            "trodde du kunne snike deg forbi?", "skatten er MIN", "go go go", "ez kill incoming"};
    private static final String[] DREPT = {"ez", "gg ez", "L", "for lett", "get good", "rip", "noob lol", "gg"};
    private static final String[] DOD = {"gg", "lag!!", "hacker", "wtf", "ok du er god", "neiii", "min wifi..."};
    private static final String[] SPISER = {"gapple time", "brb healer", "nam nam"};

    private final RangedBowAttackGoal<VaktEntity> bueMaal = new RangedBowAttackGoal<>(this, 1.0, 20, 15.0f);
    private final MeleeAttackGoal naerMaal = new MeleeAttackGoal(this, 1.25, true);

    private boolean utstyrt;
    private int epler = 2;
    private int spiseNedtelling;
    private int byttNedtelling;
    private boolean spiser;
    private ItemStack lagretVaapen = ItemStack.EMPTY;

    public VaktEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 10;
        this.setPersistenceRequired();
        this.setCanPickUpLoot(false);
        this.byttVaapenMaal();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20.0)
                .add(Attributes.MOVEMENT_SPEED, 0.3)
                .add(Attributes.ATTACK_DAMAGE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 40.0);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 16.0f));
        this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    /** Som skjelettene: bue i hånda = bue-AI, ellers nærkamp. */
    private void byttVaapenMaal() {
        if (this.level() == null || this.level().isClientSide || this.naerMaal == null || this.bueMaal == null) return;
        this.goalSelector.removeGoal(this.naerMaal);
        this.goalSelector.removeGoal(this.bueMaal);
        if (this.spiser) return;
        if (this.getMainHandItem().is(Items.BOW)) {
            this.goalSelector.addGoal(4, this.bueMaal);
        } else {
            this.goalSelector.addGoal(4, this.naerMaal);
        }
    }

    @Override
    public void setItemSlot(EquipmentSlot slot, ItemStack stack) {
        super.setItemSlot(slot, stack);
        if (slot == EquipmentSlot.MAINHAND && this.level() != null && !this.level().isClientSide) {
            this.byttVaapenMaal();
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.utstyrt && !this.level().isClientSide) utstyr();
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
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
            this.jumpFromGround();   // hopp for kritisk treff, som en ekte spiller
        }
        if (!bue && avstand < 16 && this.onGround() && this.random.nextInt(18) == 0) {
            Vec3 mot = maal.position().subtract(this.position()).normalize();
            Vec3 side = new Vec3(-mot.z, 0, mot.x).scale(this.random.nextBoolean() ? 0.35 : -0.35);
            this.setDeltaMovement(this.getDeltaMovement().add(side));   // strafe
        }
    }

    private ItemStack hentVaapen() {
        ItemStack v = this.lagretVaapen.isEmpty() ? new ItemStack(Items.IRON_SWORD) : this.lagretVaapen;
        this.lagretVaapen = ItemStack.EMPTY;
        return v;
    }

    private void begynnAaSpise(LivingEntity maal) {
        if (!this.getMainHandItem().is(Items.GOLDEN_APPLE)) {
            ItemStack naa = this.getMainHandItem().copy();
            this.lagretVaapen = naa.is(Items.BOW) ? this.lagretVaapen : naa;
        }
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
        if (!this.hasCustomName()) {
            this.setCustomName(Component.literal(velg(NAVN)));
        }
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
        for (EquipmentSlot s : EquipmentSlot.values()) {
            this.setDropChance(s, 0.0f);
        }
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
        Arrow pil = new Arrow(this.level(), this, new ItemStack(Items.ARROW), bue);
        pil.pickup = AbstractArrow.Pickup.DISALLOWED;
        double dx = target.getX() - this.getX();
        double dy = target.getY(0.3333) - pil.getY();
        double dz = target.getZ() - this.getZ();
        double h = Math.sqrt(dx * dx + dz * dz);
        pil.shoot(dx, dy + h * 0.2, dz, 1.8f, 10 - this.level().getDifficulty().getId() * 3);
        pil.setBaseDamage(pil.getBaseDamage() + 1.0);
        this.playSound(SoundEvents.ARROW_SHOOT, 1.0f, 1.0f / (this.getRandom().nextFloat() * 0.4f + 0.8f));
        this.level().addFreshEntity(pil);
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean kritisk = !this.onGround() && this.fallDistance > 0.0f;
        boolean traff = super.doHurtTarget(target);
        if (traff && kritisk && target instanceof LivingEntity levende && this.level() instanceof ServerLevel sl) {
            levende.invulnerableTime = 0;
            levende.hurt(this.damageSources().mobAttack(this), 3.0f);
            sl.getChunkSource().broadcastAndSend(this, new ClientboundAnimatePacket(target, ClientboundAnimatePacket.CRITICAL_HIT));
            this.playSound(SoundEvents.PLAYER_ATTACK_CRIT, 1.0f, 1.0f);
        }
        return traff;
    }

    @Override
    public void setTarget(@Nullable LivingEntity target) {
        LivingEntity foer = this.getTarget();
        super.setTarget(target);
        if (target instanceof Player && foer == null && !this.level().isClientSide && this.random.nextInt(3) == 0) {
            chat(velg(HEI));
        }
    }

    @Override
    public boolean killedEntity(ServerLevel level, LivingEntity offer) {
        if (offer instanceof Player) chat(velg(DREPT));
        return super.killedEntity(level, offer);
    }

    @Override
    public void die(DamageSource kilde) {
        if (!this.level().isClientSide && this.random.nextInt(2) == 0) chat(velg(DOD));
        super.die(kilde);
    }

    private void chat(String melding) {
        if (this.getServer() != null) {
            this.getServer().getPlayerList().broadcastSystemMessage(
                    Component.literal("<" + this.getName().getString() + "> " + melding), false);
        }
    }

    private String velg(String[] liste) {
        return liste[this.random.nextInt(liste.length)];
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource kilde) {
        return SoundEvents.PLAYER_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.PLAYER_DEATH;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Utstyrt", this.utstyrt);
        tag.putInt("Epler", this.epler);
        if (!this.lagretVaapen.isEmpty()) {
            tag.put("LagretVaapen", this.lagretVaapen.save(this.registryAccess()));
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.utstyrt = tag.getBoolean("Utstyrt");
        if (tag.contains("Epler")) this.epler = tag.getInt("Epler");
        if (tag.contains("LagretVaapen")) {
            this.lagretVaapen = ItemStack.parse(this.registryAccess(), tag.get("LagretVaapen")).orElse(ItemStack.EMPTY);
        }
        this.byttVaapenMaal();
    }
}
