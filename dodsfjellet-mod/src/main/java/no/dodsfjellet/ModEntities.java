package no.dodsfjellet;

import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

public final class ModEntities {
    private ModEntities() {}

    public static final EntityType<VaktEntity> VAKT = Registry.register(BuiltInRegistries.ENTITY_TYPE,
            Dodsfjellet.id("vakt"),
            EntityType.Builder.of(VaktEntity::new, MobCategory.MONSTER)
                    .sized(0.6f, 1.8f)
                    .eyeHeight(1.62f)
                    .clientTrackingRange(10)
                    .build("vakt"));

    public static void register() {
        FabricDefaultAttributeRegistry.register(VAKT, VaktEntity.createAttributes());
    }
}
