package no.dodsfjellet.client;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.item.v1.ItemTooltipCallback;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import no.dodsfjellet.ModEntiteter;
import no.dodsfjellet.ModGjenstander;

public class DodsfjelletClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        EntityRendererRegistry.register(ModEntiteter.VAKT, VaktRenderer::new);

        ItemTooltipCallback.EVENT.register((stack, ctx, flagg, linjer) -> {
            Integer nivaa = stack.get(ModGjenstander.OPPGRADERING);
            if (nivaa != null && nivaa > 0) {
                linjer.add(1, Component.literal("★ Oppgradert +" + nivaa).withStyle(nivaa >= 10 ? ChatFormatting.GOLD
                        : nivaa >= 5 ? ChatFormatting.LIGHT_PURPLE : ChatFormatting.AQUA));
            }
        });
    }
}
