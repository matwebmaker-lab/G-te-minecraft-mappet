package no.dodsfjellet.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.HumanoidArmorModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.client.resources.DefaultPlayerSkin;
import net.minecraft.client.resources.PlayerSkin;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import no.dodsfjellet.VaktEntity;

/** Tegner vakten med spillermodell (bred eller smal) og en standard spiller-skin valgt ut fra UUID-en. */
public class VaktRenderer extends HumanoidMobRenderer<VaktEntity, PlayerModel<VaktEntity>> {
    private final PlayerModel<VaktEntity> bred;
    private final PlayerModel<VaktEntity> smal;

    public VaktRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new PlayerModel<>(ctx.bakeLayer(ModelLayers.PLAYER), false), 0.5f);
        this.bred = this.model;
        this.smal = new PlayerModel<>(ctx.bakeLayer(ModelLayers.PLAYER_SLIM), true);
        this.addLayer(new HumanoidArmorLayer<>(this,
                new HumanoidArmorModel<>(ctx.bakeLayer(ModelLayers.PLAYER_INNER_ARMOR)),
                new HumanoidArmorModel<>(ctx.bakeLayer(ModelLayers.PLAYER_OUTER_ARMOR)),
                ctx.getModelManager()));
    }

    @Override
    public void render(VaktEntity vakt, float yaw, float delta, PoseStack pose, MultiBufferSource buffers, int lys) {
        PlayerSkin skin = DefaultPlayerSkin.get(vakt.getUUID());
        this.model = skin.model() == PlayerSkin.Model.SLIM ? this.smal : this.bred;
        this.model.rightArmPose = armPose(vakt);
        this.model.leftArmPose = HumanoidModel.ArmPose.EMPTY;
        super.render(vakt, yaw, delta, pose, buffers, lys);
    }

    private static HumanoidModel.ArmPose armPose(VaktEntity vakt) {
        ItemStack hand = vakt.getMainHandItem();
        if (hand.isEmpty()) return HumanoidModel.ArmPose.EMPTY;
        if (hand.is(Items.BOW) && vakt.isAggressive()) return HumanoidModel.ArmPose.BOW_AND_ARROW;
        return HumanoidModel.ArmPose.ITEM;
    }

    @Override
    public ResourceLocation getTextureLocation(VaktEntity vakt) {
        return DefaultPlayerSkin.get(vakt.getUUID()).texture();
    }
}
