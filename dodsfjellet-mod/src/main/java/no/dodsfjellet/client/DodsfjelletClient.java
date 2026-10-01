package no.dodsfjellet.client;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import no.dodsfjellet.ModEntities;

public class DodsfjelletClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        EntityRendererRegistry.register(ModEntities.VAKT, VaktRenderer::new);
    }
}
