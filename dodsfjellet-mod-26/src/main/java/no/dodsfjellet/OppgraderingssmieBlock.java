package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jspecify.annotations.Nullable;

/**
 * Oppgraderingssmia: hold et våpen eller en rustningsdel og høyreklikk.
 * Hvert nivå (opptil +10) koster nivå+1 dødskrystaller og gjør gjenstanden sterkere enn spillet egentlig tillater:
 * mer skade/rustning/liv og fortryllelser over maks (Skarphet X, Beskyttelse X).
 */
public class OppgraderingssmieBlock extends Block {
    public static final int MAKS = 10;

    public OppgraderingssmieBlock(Properties props) {
        super(props);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player spiller, BlockHitResult hit) {
        if (!level.isClientSide()) {
            spiller.sendSystemMessage(Component.literal("⚒ Oppgraderingssmia").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD));
            spiller.sendSystemMessage(Component.literal("Hold et våpen eller en rustningsdel og høyreklikk smia.").withStyle(ChatFormatting.GRAY));
            spiller.sendSystemMessage(Component.literal("Nivå +1 til +10. Hvert nivå koster (nivå+1) dødskrystaller.").withStyle(ChatFormatting.GRAY));
            spiller.sendSystemMessage(Component.literal("+5 våpen: livstyveri.  +10 våpen: Dødsstøt hvert 4. slag.").withStyle(ChatFormatting.LIGHT_PURPLE));
            spiller.sendSystemMessage(Component.literal("Rustning: sum +20 gir fart, sum +40 gir Udødelighet.").withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player spiller,
                                          InteractionHand hand, BlockHitResult hit) {
        if (stack.isEmpty()) return InteractionResult.PASS;
        if (!(level instanceof ServerLevel sl)) return InteractionResult.SUCCESS;
        Type type = type(stack);
        if (type == null) {
            spiller.sendSystemMessage(Component.literal("Smia kan bare oppgradere våpen og rustning.").withStyle(ChatFormatting.RED));
            return InteractionResult.FAIL;
        }
        int naa = nivaa(stack);
        if (naa >= MAKS) {
            spiller.sendSystemMessage(Component.literal("Denne er allerede maks oppgradert (+" + MAKS + ").").withStyle(ChatFormatting.GOLD));
            return InteractionResult.FAIL;
        }
        int pris = naa + 1;
        if (!spiller.getAbilities().instabuild && !betal(spiller, pris)) {
            spiller.sendSystemMessage(Component.literal("Du trenger " + pris + " dødskrystaller for +" + (naa + 1) + ".").withStyle(ChatFormatting.RED));
            return InteractionResult.FAIL;
        }
        oppgrader(sl, stack, naa + 1, type);
        sl.playSound(null, pos, SoundEvents.SMITHING_TABLE_USE, SoundSource.BLOCKS, 1.0f, 0.7f);
        sl.playSound(null, pos, SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.BLOCKS, 1.0f, 0.6f);
        sl.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5, 25, 0.3, 0.2, 0.3, 0.03);
        sl.sendParticles(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 1.5, pos.getZ() + 0.5, 40, 0.4, 0.6, 0.4, 0.5);
        spiller.sendOverlayMessage(Component.empty().append(stack.getHoverName()).append(
                Component.literal(" er nå +" + (naa + 1) + "!").withStyle(ChatFormatting.LIGHT_PURPLE)));
        return InteractionResult.SUCCESS;
    }

    enum Type { VAAPEN, RUSTNING }

    static @Nullable Type type(ItemStack stack) {
        Equippable eq = stack.get(DataComponents.EQUIPPABLE);
        if (eq != null && eq.slot().isArmor() && eq.slot() != EquipmentSlot.BODY) return Type.RUSTNING;
        ItemAttributeModifiers mods = stack.getItem().components().getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
        for (ItemAttributeModifiers.Entry e : mods.modifiers()) {
            if (e.attribute().equals(Attributes.ATTACK_DAMAGE)) return Type.VAAPEN;
        }
        return null;
    }

    public static int nivaa(ItemStack stack) {
        return stack.getOrDefault(ModGjenstander.OPPGRADERING, 0);
    }

    private static boolean betal(Player p, int pris) {
        int har = 0;
        var inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            if (inv.getItem(i).is(ModGjenstander.DODSKRYSTALL)) har += inv.getItem(i).getCount();
        }
        if (har < pris) return false;
        for (int i = 0; i < inv.getContainerSize() && pris > 0; i++) {
            ItemStack s = inv.getItem(i);
            if (s.is(ModGjenstander.DODSKRYSTALL)) {
                int ta = Math.min(pris, s.getCount());
                s.shrink(ta);
                pris -= ta;
            }
        }
        return true;
    }

    static void oppgrader(ServerLevel sl, ItemStack stack, int nivaa, Type type) {
        stack.set(ModGjenstander.OPPGRADERING, nivaa);
        ItemAttributeModifiers mods = stack.getItem().components().getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
        var reg = sl.registryAccess().lookupOrThrow(Registries.ENCHANTMENT);
        if (type == Type.VAAPEN) {
            mods = mods.withModifierAdded(Attributes.ATTACK_DAMAGE,
                    new AttributeModifier(Reg.id("oppgradering_skade"), nivaa * 1.0, AttributeModifier.Operation.ADD_VALUE),
                    EquipmentSlotGroup.MAINHAND);
            mods = mods.withModifierAdded(Attributes.ATTACK_SPEED,
                    new AttributeModifier(Reg.id("oppgradering_fart"), nivaa * 0.05, AttributeModifier.Operation.ADD_VALUE),
                    EquipmentSlotGroup.MAINHAND);
            Holder<Enchantment> skarphet = reg.getOrThrow(Enchantments.SHARPNESS);
            EnchantmentHelper.updateEnchantments(stack, m -> m.set(skarphet, Math.max(m.getLevel(skarphet), nivaa)));
        } else {
            EquipmentSlot slot = stack.get(DataComponents.EQUIPPABLE).slot();
            EquipmentSlotGroup gruppe = EquipmentSlotGroup.bySlot(slot);
            String s = slot.getName();
            mods = mods.withModifierAdded(Attributes.ARMOR,
                    new AttributeModifier(Reg.id("oppgradering_rustning_" + s), nivaa * 0.5, AttributeModifier.Operation.ADD_VALUE), gruppe);
            mods = mods.withModifierAdded(Attributes.ARMOR_TOUGHNESS,
                    new AttributeModifier(Reg.id("oppgradering_seighet_" + s), nivaa * 0.5, AttributeModifier.Operation.ADD_VALUE), gruppe);
            mods = mods.withModifierAdded(Attributes.MAX_HEALTH,
                    new AttributeModifier(Reg.id("oppgradering_liv_" + s), nivaa * 0.5, AttributeModifier.Operation.ADD_VALUE), gruppe);
            Holder<Enchantment> beskyttelse = reg.getOrThrow(Enchantments.PROTECTION);
            EnchantmentHelper.updateEnchantments(stack, m -> m.set(beskyttelse, Math.max(m.getLevel(beskyttelse), nivaa)));
        }
        stack.set(DataComponents.ATTRIBUTE_MODIFIERS, mods);
    }
}
