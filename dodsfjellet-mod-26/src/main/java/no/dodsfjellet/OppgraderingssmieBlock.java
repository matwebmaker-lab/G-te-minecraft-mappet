package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.ItemTags;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.MaceItem;
import net.minecraft.world.item.TridentItem;
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

import java.util.LinkedHashMap;
import java.util.Map;

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
            spiller.sendSystemMessage(Component.literal("Hold et våpen, verktøy, en bue, et gevær eller en rustningsdel og høyreklikk.").withStyle(ChatFormatting.GRAY));
            spiller.sendSystemMessage(Component.literal("Nivå +1 til +10. Hvert nivå koster (nivå+1) dødskrystaller.").withStyle(ChatFormatting.GRAY));
            spiller.sendSystemMessage(Component.literal("Sverd: Skarphet, Plyndring, Ild.  Hakke/spade/ljå: Effektivitet, Flaks, raskere graving.").withStyle(ChatFormatting.GRAY));
            spiller.sendSystemMessage(Component.literal("Bue: Kraft, Slag, Flamme, Uendelig.  Gevær: skade, magasin, omlading.").withStyle(ChatFormatting.GRAY));
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
            spiller.sendSystemMessage(Component.literal("Smia kan bare oppgradere våpen, verktøy og rustning.").withStyle(ChatFormatting.RED));
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

    /** Hva slags gjenstand det er – avgjør hvilke fortryllelser og egenskaper smia gir. */
    enum Type { SVERD, OKS, VERKTOY, BUE, ARMBROST, TREFORK, STRIDSKOLLE, GEVAER, RUSTNING }

    static @Nullable Type type(ItemStack stack) {
        Equippable eq = stack.get(DataComponents.EQUIPPABLE);
        if (eq != null && eq.slot().isArmor() && eq.slot() != EquipmentSlot.BODY) return Type.RUSTNING;
        if (stack.getItem() instanceof GevaerItem) return Type.GEVAER;
        if (stack.is(ItemTags.AXES)) return Type.OKS;
        if (stack.is(ItemTags.PICKAXES) || stack.is(ItemTags.SHOVELS) || stack.is(ItemTags.HOES)) return Type.VERKTOY;
        if (stack.getItem() instanceof BowItem) return Type.BUE;
        if (stack.getItem() instanceof CrossbowItem) return Type.ARMBROST;
        if (stack.getItem() instanceof TridentItem) return Type.TREFORK;
        if (stack.getItem() instanceof MaceItem) return Type.STRIDSKOLLE;
        if (stack.is(ItemTags.SWORDS) || stack.is(ItemTags.SPEARS)) return Type.SVERD;
        ItemAttributeModifiers mods = stack.getItem().components().getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
        for (ItemAttributeModifiers.Entry e : mods.modifiers()) {
            if (e.attribute().equals(Attributes.ATTACK_DAMAGE)) return Type.SVERD;   // våre egne våpen
        }
        return null;
    }

    public static int nivaa(ItemStack stack) {
        return stack.getOrDefault(ModGjenstander.OPPGRADERING, 0);
    }

    /** Oppgraderingsnivået, men bare for nærkampvåpen (livstyveri og Dødsstøt). */
    public static int naerkampNivaa(ItemStack stack) {
        Type t = type(stack);
        return t == Type.SVERD || t == Type.OKS || t == Type.TREFORK || t == Type.STRIDSKOLLE ? nivaa(stack) : 0;
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
        Map<ResourceKey<Enchantment>, Integer> fort = new LinkedHashMap<>();
        switch (type) {
            case SVERD -> {
                mods = haand(mods, Attributes.ATTACK_DAMAGE, "skade", nivaa * 1.0);
                mods = haand(mods, Attributes.ATTACK_SPEED, "fart", nivaa * 0.05);
                fort.put(Enchantments.SHARPNESS, nivaa);
                if (nivaa >= 3) fort.put(Enchantments.LOOTING, Math.min(5, nivaa / 2));
                if (nivaa >= 6) fort.put(Enchantments.FIRE_ASPECT, nivaa >= 9 ? 3 : 2);
            }
            case OKS -> {   // både våpen og verktøy
                mods = haand(mods, Attributes.ATTACK_DAMAGE, "skade", nivaa * 0.8);
                mods = haand(mods, Attributes.MINING_EFFICIENCY, "graving", nivaa * 3.0);
                fort.put(Enchantments.SHARPNESS, (nivaa + 1) / 2);
                fort.put(Enchantments.EFFICIENCY, nivaa);
            }
            case VERKTOY -> {
                mods = haand(mods, Attributes.MINING_EFFICIENCY, "graving", nivaa * 3.0);
                mods = haand(mods, Attributes.BLOCK_INTERACTION_RANGE, "rekkevidde", nivaa * 0.2);
                fort.put(Enchantments.EFFICIENCY, nivaa);
                if (nivaa >= 2) fort.put(Enchantments.FORTUNE, Math.min(5, nivaa / 2));
            }
            case BUE -> {
                fort.put(Enchantments.POWER, nivaa);
                if (nivaa >= 3) fort.put(Enchantments.PUNCH, Math.min(4, nivaa / 3));
                if (nivaa >= 5) fort.put(Enchantments.FLAME, 1);
                if (nivaa >= 8) fort.put(Enchantments.INFINITY, 1);
            }
            case ARMBROST -> {
                fort.put(Enchantments.QUICK_CHARGE, Math.min(5, (nivaa + 1) / 2));
                fort.put(Enchantments.PIERCING, nivaa);
                if (nivaa >= 6) fort.put(Enchantments.MULTISHOT, 1);
            }
            case TREFORK -> {
                mods = haand(mods, Attributes.ATTACK_DAMAGE, "skade", nivaa * 1.0);
                fort.put(Enchantments.IMPALING, nivaa);
                fort.put(Enchantments.LOYALTY, Math.min(5, (nivaa + 1) / 2));
                if (nivaa >= 6) fort.put(Enchantments.CHANNELING, 1);
            }
            case STRIDSKOLLE -> {
                mods = haand(mods, Attributes.ATTACK_DAMAGE, "skade", nivaa * 0.8);
                fort.put(Enchantments.DENSITY, nivaa);
                if (nivaa >= 4) fort.put(Enchantments.BREACH, Math.min(6, nivaa / 2));
                if (nivaa >= 7) fort.put(Enchantments.WIND_BURST, Math.min(4, nivaa / 3));
            }
            case GEVAER -> {}   // GevaerItem leser nivået selv: mer skade, raskere omlading, større magasin
            case RUSTNING -> {
                EquipmentSlot slot = stack.get(DataComponents.EQUIPPABLE).slot();
                EquipmentSlotGroup gruppe = EquipmentSlotGroup.bySlot(slot);
                String s = slot.getName();
                mods = mods.withModifierAdded(Attributes.ARMOR,
                        new AttributeModifier(Reg.id("oppgradering_rustning_" + s), nivaa * 0.5, AttributeModifier.Operation.ADD_VALUE), gruppe);
                mods = mods.withModifierAdded(Attributes.ARMOR_TOUGHNESS,
                        new AttributeModifier(Reg.id("oppgradering_seighet_" + s), nivaa * 0.5, AttributeModifier.Operation.ADD_VALUE), gruppe);
                mods = mods.withModifierAdded(Attributes.MAX_HEALTH,
                        new AttributeModifier(Reg.id("oppgradering_liv_" + s), nivaa * 0.5, AttributeModifier.Operation.ADD_VALUE), gruppe);
                fort.put(Enchantments.PROTECTION, nivaa);
                if (slot == EquipmentSlot.FEET) fort.put(Enchantments.FEATHER_FALLING, nivaa);
                if (slot == EquipmentSlot.HEAD && nivaa >= 3) fort.put(Enchantments.RESPIRATION, Math.min(5, nivaa / 2));
            }
        }
        if (stack.isDamageableItem()) fort.put(Enchantments.UNBREAKING, Math.min(10, (nivaa + 1) / 2 + 1));
        if (nivaa >= 10 && stack.isDamageableItem()) fort.put(Enchantments.MENDING, 1);
        for (var e : fort.entrySet()) {
            Holder<Enchantment> h = reg.getOrThrow(e.getKey());
            int niv = e.getValue();
            EnchantmentHelper.updateEnchantments(stack, m -> m.set(h, Math.max(m.getLevel(h), niv)));
        }
        if (type != Type.GEVAER) stack.set(DataComponents.ATTRIBUTE_MODIFIERS, mods);
        if (stack.isDamageableItem()) stack.setDamageValue(0);   // smia reparerer også
    }

    private static ItemAttributeModifiers haand(ItemAttributeModifiers mods, Holder<Attribute> attr, String navn, double verdi) {
        return mods.withModifierAdded(attr, new AttributeModifier(Reg.id("oppgradering_" + navn), verdi, AttributeModifier.Operation.ADD_VALUE),
                EquipmentSlotGroup.MAINHAND);
    }
}
