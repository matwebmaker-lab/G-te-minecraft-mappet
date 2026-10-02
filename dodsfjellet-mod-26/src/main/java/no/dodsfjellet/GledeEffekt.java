package no.dodsfjellet;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;

/** Glede: små hjerter rundt deg og litt helbreding hvert sekund. */
public class GledeEffekt extends MobEffect {
    public GledeEffekt() {
        super(MobEffectCategory.BENEFICIAL, 0xFFD84A);
    }

    @Override
    public boolean shouldApplyEffectTickThisTick(int tick, int nivaa) {
        return tick % 20 == 0;
    }

    @Override
    public boolean applyEffectTick(ServerLevel sl, LivingEntity mob, int nivaa) {
        if (mob.getHealth() < mob.getMaxHealth()) mob.heal(1.0f + nivaa);
        sl.sendParticles(ParticleTypes.HEART, mob.getX(), mob.getY() + mob.getBbHeight() + 0.3, mob.getZ(), 2, 0.35, 0.2, 0.35, 0);
        sl.sendParticles(ParticleTypes.HAPPY_VILLAGER, mob.getX(), mob.getY() + 1, mob.getZ(), 4, 0.4, 0.5, 0.4, 0);
        return true;
    }
}
