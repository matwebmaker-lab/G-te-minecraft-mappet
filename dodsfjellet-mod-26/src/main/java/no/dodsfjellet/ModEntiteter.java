package no.dodsfjellet;

import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;

public final class ModEntiteter {
    private ModEntiteter() {}

    private static final ResourceKey<EntityType<?>> VAKT_KEY = ResourceKey.create(Registries.ENTITY_TYPE, Reg.id("vakt"));

    public static final EntityType<VaktEntity> VAKT = Registry.register(BuiltInRegistries.ENTITY_TYPE, VAKT_KEY,
            EntityType.Builder.of(VaktEntity::new, MobCategory.MONSTER)
                    .sized(0.6f, 1.8f).eyeHeight(1.62f).clientTrackingRange(10).build(VAKT_KEY));

    public static void register() {
        FabricDefaultAttributeRegistry.register(VAKT, VaktEntity.createAttributes());
        // Som zombier: bare på fast grunn i mørke (ellers spawner de oppå lavahavet i Dødsriket)
        SpawnPlacements.register(VAKT, SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkMonsterSpawnRules);
    }
}
