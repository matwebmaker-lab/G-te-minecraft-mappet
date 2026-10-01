package no.dodsfjellet;

import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.ChatFormatting;

import java.util.EnumMap;
import java.util.List;

public final class ModItems {
    private ModItems() {}

    public static final Holder<ArmorMaterial> FJELLVOKTER_MATERIALE = registrerMateriale();

    /** Gåte 1-belønning: rask dolk som gjør fienden treg og deg rask. */
    public static final Item SKYGGEDOLK = reg("skyggedolk", new SkyggedolkItem(new Item.Properties()
            .attributes(SwordItem.createAttributes(Tiers.DIAMOND, 2, -1.6f)).rarity(Rarity.RARE)));

    /** Kodelås-belønning: tungt sverd som setter fyr på fienden og slår den langt unna. */
    public static final Item VOKTERKNUSER = reg("vokterknuser", new VokterknuserItem(new Item.Properties()
            .attributes(SwordItem.createAttributes(Tiers.NETHERITE, 7, -2.8f)).fireResistant().rarity(Rarity.EPIC)));

    public static final Item FJELLVOKTER_HJELM = reg("fjellvokter_hjelm", rustning(ArmorItem.Type.HELMET));
    public static final Item FJELLVOKTER_BRYNJE = reg("fjellvokter_brynje", rustning(ArmorItem.Type.CHESTPLATE));
    public static final Item FJELLVOKTER_BUKSER = reg("fjellvokter_bukser", rustning(ArmorItem.Type.LEGGINGS));
    public static final Item FJELLVOKTER_STOVLER = reg("fjellvokter_stovler", rustning(ArmorItem.Type.BOOTS));

    public static final Item VAKT_SPAWN_EGG = reg("vakt_spawn_egg",
            new SpawnEggItem(ModEntities.VAKT, 0x2b2b33, 0xb02020, new Item.Properties()));

    private static Item rustning(ArmorItem.Type type) {
        return new ArmorItem(FJELLVOKTER_MATERIALE, type, new Item.Properties()
                .durability(type.getDurability(40)).fireResistant().rarity(Rarity.EPIC));
    }

    private static Holder<ArmorMaterial> registrerMateriale() {
        EnumMap<ArmorItem.Type, Integer> forsvar = new EnumMap<>(ArmorItem.Type.class);
        forsvar.put(ArmorItem.Type.BOOTS, 4);
        forsvar.put(ArmorItem.Type.LEGGINGS, 7);
        forsvar.put(ArmorItem.Type.CHESTPLATE, 9);
        forsvar.put(ArmorItem.Type.HELMET, 4);
        forsvar.put(ArmorItem.Type.BODY, 12);
        return Registry.registerForHolder(BuiltInRegistries.ARMOR_MATERIAL, Dodsfjellet.id("fjellvokter"),
                new ArmorMaterial(forsvar, 18, SoundEvents.ARMOR_EQUIP_NETHERITE,
                        () -> Ingredient.of(Items.NETHERITE_INGOT),
                        List.of(new ArmorMaterial.Layer(Dodsfjellet.id("fjellvokter"))),
                        3.5f, 0.15f));
    }

    private static Item reg(String navn, Item item) {
        return Registry.register(BuiltInRegistries.ITEM, Dodsfjellet.id(navn), item);
    }

    public static void register() {
        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.COMBAT).register(e -> {
            e.accept(SKYGGEDOLK);
            e.accept(VOKTERKNUSER);
            e.accept(FJELLVOKTER_HJELM);
            e.accept(FJELLVOKTER_BRYNJE);
            e.accept(FJELLVOKTER_BUKSER);
            e.accept(FJELLVOKTER_STOVLER);
        });
        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.SPAWN_EGGS).register(e -> e.accept(VAKT_SPAWN_EGG));
    }

    static void tooltip(List<Component> tooltip, String tekst) {
        tooltip.add(Component.literal(tekst).withStyle(ChatFormatting.GRAY));
    }

    public static class SkyggedolkItem extends SwordItem {
        public SkyggedolkItem(Item.Properties props) {
            super(Tiers.DIAMOND, props);
        }

        @Override
        public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 50, 1));
            attacker.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 50, 0));
            return super.hurtEnemy(stack, target, attacker);
        }

        @Override
        public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> tooltip, TooltipFlag flag) {
            tooltip(tooltip, "Belønning for gåte 1");
            tooltip(tooltip, "Treff: fienden blir treg, du blir rask");
        }
    }

    public static class VokterknuserItem extends SwordItem {
        public VokterknuserItem(Item.Properties props) {
            super(Tiers.NETHERITE, props);
        }

        @Override
        public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
            target.igniteForSeconds(4);
            target.knockback(1.4, attacker.getX() - target.getX(), attacker.getZ() - target.getZ());
            return super.hurtEnemy(stack, target, attacker);
        }

        @Override
        public void appendHoverText(ItemStack stack, Item.TooltipContext ctx, List<Component> tooltip, TooltipFlag flag) {
            tooltip(tooltip, "Belønning for kodelåsen");
            tooltip(tooltip, "Treff: setter fyr på fienden og slår den langt unna");
        }
    }
}
