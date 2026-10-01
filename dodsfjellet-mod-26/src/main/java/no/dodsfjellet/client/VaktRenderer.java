package no.dodsfjellet.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.player.PlayerModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.ArmorModelSet;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.client.renderer.entity.state.AvatarRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.resources.DefaultPlayerSkin;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.PlayerModelType;
import net.minecraft.world.item.Items;
import no.dodsfjellet.VaktEntity;

/**
 * Tegner vakten som en spiller: bred eller smal spillermodell og en standard spiller-skin valgt fra UUID-en.
 * Bygger på MobRenderer (ikke HumanoidMobRenderer), så vi kan bytte modell per skin.
 */
public class VaktRenderer extends MobRenderer<VaktEntity, AvatarRenderState, PlayerModel> {
    private final PlayerModel bred;
    private final PlayerModel smal;

    public VaktRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new PlayerModel(ctx.bakeLayer(ModelLayers.PLAYER), false), 0.5f);
        this.bred = this.model;
        this.smal = new PlayerModel(ctx.bakeLayer(ModelLayers.PLAYER_SLIM), true);
        this.addLayer(new HumanoidArmorLayer<>(this,
                ArmorModelSet.bake(ModelLayers.PLAYER_ARMOR, ctx.getModelSet(), del -> new PlayerModel(del, false)),
                ctx.getEquipmentRenderer()));
        this.addLayer(new ItemInHandLayer<>(this));
    }

    @Override
    public AvatarRenderState createRenderState() {
        return new AvatarRenderState();
    }

    @Override
    public void extractRenderState(VaktEntity vakt, AvatarRenderState state, float delta) {
        super.extractRenderState(vakt, state, delta);
        HumanoidMobRenderer.extractHumanoidRenderState(vakt, state, delta, this.itemModelResolver);
        state.skin = DefaultPlayerSkin.get(vakt.getUUID());
        HumanoidModel.ArmPose arm = vakt.getMainHandItem().isEmpty() ? HumanoidModel.ArmPose.EMPTY
                : (vakt.getMainHandItem().is(Items.BOW) && vakt.isAggressive()) ? HumanoidModel.ArmPose.BOW_AND_ARROW
                : HumanoidModel.ArmPose.ITEM;
        state.rightArmPose = arm;
        state.leftArmPose = HumanoidModel.ArmPose.EMPTY;
        state.showHat = true;
        state.showJacket = true;
        state.showLeftSleeve = true;
        state.showRightSleeve = true;
        state.showLeftPants = true;
        state.showRightPants = true;
    }

    @Override
    public void submit(AvatarRenderState state, PoseStack pose, SubmitNodeCollector samler, CameraRenderState kamera) {
        this.model = state.skin.model() == PlayerModelType.SLIM ? this.smal : this.bred;
        super.submit(state, pose, samler, kamera);
    }

    @Override
    public Identifier getTextureLocation(AvatarRenderState state) {
        return state.skin.body().texturePath();
    }
}
