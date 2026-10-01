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

/** Reisekompasset: høyreklikk for en klikkbar meny som teleporterer deg hvor du vil. */
public class ReisekompassItem extends Item {
    public ReisekompassItem(Item.Properties p) {
        super(p);
    }

    @Override
    public InteractionResult use(Level level, Player spiller, InteractionHand hand) {
        if (spiller instanceof ServerPlayer sp) Reise.visMeny(sp);
        return InteractionResult.SUCCESS;
    }

    @Override
    @SuppressWarnings("deprecation")
    public void appendHoverText(ItemStack s, Item.TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
        ut.accept(Component.literal("Høyreklikk: reisemeny – Dødsfjellet, Dødsriket og PvP-øya").withStyle(ChatFormatting.GRAY));
    }
}
