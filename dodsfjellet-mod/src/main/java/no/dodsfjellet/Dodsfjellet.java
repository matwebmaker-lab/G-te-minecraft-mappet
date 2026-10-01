package no.dodsfjellet;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;

public class Dodsfjellet implements ModInitializer {
    public static final String MOD_ID = "dodsfjellet";

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }

    @Override
    public void onInitialize() {
        ModEntities.register();
        ModItems.register();

        // Fjellvokter-settet: har du alle fire delene på, får du styrke, motstand og nattsyn.
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 20 != 0) return;
            for (ServerPlayer p : server.getPlayerList().getPlayers()) {
                if (harFulltSett(p)) {
                    p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 60, 0, true, false, true));
                    p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false, true));
                    p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 260, 0, true, false, true));
                }
            }
        });
    }

    private static boolean harFulltSett(ServerPlayer p) {
        return p.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.FJELLVOKTER_HJELM)
                && p.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.FJELLVOKTER_BRYNJE)
                && p.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.FJELLVOKTER_BUKSER)
                && p.getItemBySlot(EquipmentSlot.FEET).is(ModItems.FJELLVOKTER_STOVLER);
    }
}
