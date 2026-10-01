package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/** Dødsnøkkelen: høyreklikk for å reise til Dødsriket – og tilbake igjen. */
public class DodsnokkelItem extends Item {
    public DodsnokkelItem(Item.Properties p) {
        super(p);
    }

    @Override
    public InteractionResult use(Level level, Player spiller, InteractionHand hand) {
        ItemStack stack = spiller.getItemInHand(hand);
        if (spiller.getCooldowns().isOnCooldown(stack)) return InteractionResult.FAIL;
        if (spiller instanceof ServerPlayer sp) {
            if (level.dimension().equals(Reise.DODSRIKET)) Reise.tilOververden(sp);
            else Reise.tilDodsriket(sp);
            spiller.getCooldowns().addCooldown(stack, 100);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    @SuppressWarnings("deprecation")
    public void appendHoverText(ItemStack s, Item.TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
        ut.accept(Component.literal("Høyreklikk: reis til Dødsriket og tilbake").withStyle(ChatFormatting.GRAY));
    }
}
