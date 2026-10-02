package no.dodsfjellet.mixin.client;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.entity.player.AvatarRenderer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Avatar;
import net.minecraft.world.item.ItemStack;
import no.dodsfjellet.GevaerItem;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Spillere holder geværene med begge hender og sikter framover (samme positur som et ladd armbrøst). */
@Mixin(AvatarRenderer.class)
public class AvatarRendererMixin {
    @Inject(method = "getArmPose(Lnet/minecraft/world/entity/Avatar;Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/InteractionHand;)Lnet/minecraft/client/model/HumanoidModel$ArmPose;",
            at = @At("HEAD"), cancellable = true)
    private static void dodsfjellet$gevaerPositur(Avatar avatar, ItemStack stack, InteractionHand hand,
                                                 CallbackInfoReturnable<HumanoidModel.ArmPose> cir) {
        if (stack.getItem() instanceof GevaerItem && !avatar.isSwinging()) {
            cir.setReturnValue(HumanoidModel.ArmPose.CROSSBOW_HOLD);
        }
    }
}
