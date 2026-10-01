package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** De fire våpnene med egne evner ved treff. */
public final class Vaapen {
    private Vaapen() {}

    static void linje(Consumer<Component> ut, String tekst, ChatFormatting farge) {
        ut.accept(Component.literal(tekst).withStyle(farge));
    }

    /** Skyggedolken – gåte 1: fienden blir treg, du blir rask. */
    public static class Skyggedolk extends Item {
        public Skyggedolk(Item.Properties p) { super(p); }

        @Override
        public void hurtEnemy(ItemStack stack, LivingEntity maal, LivingEntity angriper) {
            maal.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 50, 1));
            angriper.addEffect(new MobEffectInstance(MobEffects.SPEED, 50, 0));
            super.hurtEnemy(stack, maal, angriper);
        }

        @Override
        @SuppressWarnings("deprecation")
        public void appendHoverText(ItemStack s, Item.TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
            linje(ut, "Treff: fienden blir treg, du blir rask", ChatFormatting.GRAY);
        }
    }

    /** Vokterknuseren – kodelåsen: setter fyr og slår fienden langt unna. */
    public static class Vokterknuser extends Item {
        public Vokterknuser(Item.Properties p) { super(p); }

        @Override
        public void hurtEnemy(ItemStack stack, LivingEntity maal, LivingEntity angriper) {
            maal.igniteForSeconds(4);
            Vec3 retning = maal.position().subtract(angriper.position()).normalize();
            maal.push(retning.x * 1.4, 0.45, retning.z * 1.4);
            if (maal.level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.LAVA, maal.getX(), maal.getY() + 1, maal.getZ(), 8, 0.3, 0.3, 0.3, 0.1);
            }
            super.hurtEnemy(stack, maal, angriper);
        }

        @Override
        @SuppressWarnings("deprecation")
        public void appendHoverText(ItemStack s, Item.TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
            linje(ut, "Treff: setter fyr på fienden og knuser den bakover", ChatFormatting.GRAY);
        }
    }

    /** Sjelesigden – sveiper sjeleflammer over alle rundt målet og gir wither. */
    public static class Sjelesigd extends Item {
        public Sjelesigd(Item.Properties p) { super(p); }

        @Override
        public void hurtEnemy(ItemStack stack, LivingEntity maal, LivingEntity angriper) {
            maal.addEffect(new MobEffectInstance(MobEffects.WITHER, 60, 1));
            if (maal.level() instanceof ServerLevel sl) {
                for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, maal.getBoundingBox().inflate(2.8))) {
                    if (e != angriper && e != maal && e.isAlive()) {
                        e.hurtServer(sl, sl.damageSources().indirectMagic(angriper, angriper), 4.0f);
                        e.addEffect(new MobEffectInstance(MobEffects.WITHER, 40, 0));
                    }
                }
                sl.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, maal.getX(), maal.getY() + 1, maal.getZ(), 30, 1.4, 0.4, 1.4, 0.02);
                sl.playSound(null, maal.blockPosition(), SoundEvents.SOUL_ESCAPE.value(), SoundSource.PLAYERS, 1.0f, 0.8f);
            }
            super.hurtEnemy(stack, maal, angriper);
        }

        @Override
        @SuppressWarnings("deprecation")
        public void appendHoverText(ItemStack s, Item.TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
            linje(ut, "Treff: sjeleflammer skader alle rundt målet", ChatFormatting.GRAY);
        }
    }

    /** Dødsklingen – stjeler liv for hvert slag. */
    public static class Dodsklinge extends Item {
        public Dodsklinge(Item.Properties p) { super(p); }

        @Override
        public void hurtEnemy(ItemStack stack, LivingEntity maal, LivingEntity angriper) {
            angriper.heal(2.0f);
            if (maal.level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.DAMAGE_INDICATOR, maal.getX(), maal.getY() + 1, maal.getZ(), 6, 0.3, 0.3, 0.3, 0.1);
            }
            super.hurtEnemy(stack, maal, angriper);
        }

        @Override
        @SuppressWarnings("deprecation")
        public void appendHoverText(ItemStack s, Item.TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
            linje(ut, "Treff: stjeler ett hjerte liv", ChatFormatting.GRAY);
        }
    }
}
