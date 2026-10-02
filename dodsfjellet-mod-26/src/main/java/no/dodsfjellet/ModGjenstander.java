package no.dodsfjellet;

import com.mojang.serialization.Codec;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;

import java.util.EnumMap;
import java.util.Map;

public final class ModGjenstander {
    private ModGjenstander() {}

    // ------------------------------------------------------------ komponenter og effekter
    /** Oppgraderingsnivå fra Oppgraderingssmia (0–10). */
    public static final DataComponentType<Integer> OPPGRADERING = Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE,
            Reg.id("oppgradering"), DataComponentType.<Integer>builder().persistent(Codec.intRange(0, 10))
                    .networkSynchronized(ByteBufCodecs.VAR_INT).build());

    /** Kuler i magasinet til et gevær. */
    public static final DataComponentType<Integer> MAGASIN = Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE,
            Reg.id("magasin"), DataComponentType.<Integer>builder().persistent(Codec.intRange(0, 999))
                    .networkSynchronized(ByteBufCodecs.VAR_INT).build());

    /** Blodhøst: slagene dine heler deg. */
    public static final Holder<MobEffect> BLODHOST = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT,
            Reg.id("blodhost"), new EnkelEffekt(MobEffectCategory.BENEFICIAL, 0xA3121E));

    /** Glede: hjerter og helbreding (fra Bibelen). */
    public static final Holder<MobEffect> GLEDE = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT,
            Reg.id("glede"), new GledeEffekt());

    public static class EnkelEffekt extends MobEffect {
        public EnkelEffekt(MobEffectCategory kategori, int farge) {
            super(kategori, farge);
        }
    }

    // ------------------------------------------------------------ materialer
    public static final TagKey<Item> DODSKRYSTALL_REPARASJON = TagKey.create(Registries.ITEM, Reg.id("dodskrystall_reparasjon"));
    public static final ToolMaterial DODSMETALL = new ToolMaterial(BlockTags.INCORRECT_FOR_NETHERITE_TOOL, 2600, 9.5f, 5.0f, 18,
            DODSKRYSTALL_REPARASJON);

    private static ResourceKey<EquipmentAsset> asset(String navn) {
        return ResourceKey.create(EquipmentAssets.ROOT_ID, Reg.id(navn));
    }

    private static Map<ArmorType, Integer> forsvar(int stovler, int bukser, int brynje, int hjelm, int kropp) {
        EnumMap<ArmorType, Integer> m = new EnumMap<>(ArmorType.class);
        m.put(ArmorType.BOOTS, stovler);
        m.put(ArmorType.LEGGINGS, bukser);
        m.put(ArmorType.CHESTPLATE, brynje);
        m.put(ArmorType.HELMET, hjelm);
        m.put(ArmorType.BODY, kropp);
        return m;
    }

    public static final ArmorMaterial FJELLVOKTER_MAT = new ArmorMaterial(40, forsvar(4, 7, 9, 4, 12), 18,
            SoundEvents.ARMOR_EQUIP_NETHERITE, 3.5f, 0.15f, DODSKRYSTALL_REPARASJON, asset("fjellvokter"));
    public static final ArmorMaterial SJELEPLATE_MAT = new ArmorMaterial(46, forsvar(4, 8, 10, 5, 14), 20,
            SoundEvents.ARMOR_EQUIP_NETHERITE, 4.0f, 0.2f, DODSKRYSTALL_REPARASJON, asset("sjeleplate"));

    // ------------------------------------------------------------ materialer / nøkler
    public static final Item DODSKRYSTALL = Reg.item("dodskrystall", new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final Item DODSNOKKEL = Reg.item("dodsnokkel", DodsnokkelItem::new,
            new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant());
    public static final Item REISEKOMPASS = Reg.item("reisekompass", ReisekompassItem::new,
            new Item.Properties().stacksTo(1).rarity(Rarity.RARE));

    // ------------------------------------------------------------ våpen
    public static final Item SKYGGEDOLK = Reg.item("skyggedolk", Vaapen.Skyggedolk::new,
            new Item.Properties().sword(ToolMaterial.DIAMOND, 1.0f, -1.4f).rarity(Rarity.RARE));
    public static final Item VOKTERKNUSER = Reg.item("vokterknuser", Vaapen.Vokterknuser::new,
            new Item.Properties().sword(DODSMETALL, 4.0f, -3.0f).fireResistant().rarity(Rarity.EPIC));
    public static final Item SJELESIGD = Reg.item("sjelesigd", Vaapen.Sjelesigd::new,
            new Item.Properties().sword(DODSMETALL, 3.0f, -2.6f).fireResistant().rarity(Rarity.EPIC));
    public static final Item DODSKLINGE = Reg.item("dodsklinge", Vaapen.Dodsklinge::new,
            new Item.Properties().sword(DODSMETALL, 2.5f, -2.4f).fireResistant().rarity(Rarity.EPIC));

    // ------------------------------------------------------------ glede
    public static final Item BIBEL = Reg.item("bibel", BibelItem::new, new Item.Properties().stacksTo(1).rarity(Rarity.RARE));

    // ------------------------------------------------------------ gevær og ammunisjon
    public static final Item KULER = Reg.item("kuler", new Item.Properties().stacksTo(64));
    public static final Item HAGLPATRONER = Reg.item("haglpatroner", new Item.Properties().stacksTo(64));

    private static Item gevaer(GevaerItem.Spec spec, Rarity sjeldenhet) {
        return Reg.item(spec.navn(), p -> new GevaerItem(p, spec), new Item.Properties().stacksTo(1).rarity(sjeldenhet));
    }

    //                                                       navn, skade, hagl, mag, nedkj, omlad, spredning, rekkevidde, auto, rekyl, tilbakeslag
    public static final Item PISTOL = gevaer(new GevaerItem.Spec("pistol", 6.0f, 1, 12, 5, 30, 1.6f, 60, false, 2.5f, 0,
            () -> KULER, () -> ModLyder.PISTOL, () -> ModLyder.OMLAD_PISTOL), Rarity.UNCOMMON);
    public static final Item HAGLE = gevaer(new GevaerItem.Spec("hagle", 3.2f, 9, 6, 17, 44, 9.0f, 28, false, 7.0f, 0.25f,
            () -> HAGLPATRONER, () -> ModLyder.HAGLE, () -> ModLyder.OMLAD_HAGLE), Rarity.RARE);
    public static final Item AUTOMATGEVAER = gevaer(new GevaerItem.Spec("automatgevaer", 4.5f, 1, 30, 3, 46, 2.6f, 90, true, 1.4f, 0,
            () -> KULER, () -> ModLyder.AUTOMATGEVAER, () -> ModLyder.OMLAD_AUTOMAT), Rarity.RARE);
    public static final Item SNIKSKYTTERGEVAER = gevaer(new GevaerItem.Spec("snikskyttergevaer", 24.0f, 1, 5, 30, 64, 0.15f, 220, false, 9.0f, 0.1f,
            () -> KULER, () -> ModLyder.SNIKSKYTTERGEVAER, () -> ModLyder.OMLAD_SNIKSKYTTER), Rarity.EPIC);

    // ------------------------------------------------------------ rustning
    private static Item rustning(String navn, ArmorMaterial mat, ArmorType type) {
        return Reg.item(navn, new Item.Properties().humanoidArmor(mat, type).fireResistant().rarity(Rarity.EPIC));
    }

    public static final Item FJELLVOKTER_HJELM = rustning("fjellvokter_hjelm", FJELLVOKTER_MAT, ArmorType.HELMET);
    public static final Item FJELLVOKTER_BRYNJE = rustning("fjellvokter_brynje", FJELLVOKTER_MAT, ArmorType.CHESTPLATE);
    public static final Item FJELLVOKTER_BUKSER = rustning("fjellvokter_bukser", FJELLVOKTER_MAT, ArmorType.LEGGINGS);
    public static final Item FJELLVOKTER_STOVLER = rustning("fjellvokter_stovler", FJELLVOKTER_MAT, ArmorType.BOOTS);
    public static final Item SJELEPLATE_HJELM = rustning("sjeleplate_hjelm", SJELEPLATE_MAT, ArmorType.HELMET);
    public static final Item SJELEPLATE_BRYNJE = rustning("sjeleplate_brynje", SJELEPLATE_MAT, ArmorType.CHESTPLATE);
    public static final Item SJELEPLATE_BUKSER = rustning("sjeleplate_bukser", SJELEPLATE_MAT, ArmorType.LEGGINGS);
    public static final Item SJELEPLATE_STOVLER = rustning("sjeleplate_stovler", SJELEPLATE_MAT, ArmorType.BOOTS);

    // ------------------------------------------------------------ runer (evner)
    private static Item rune(RuneItem.Evne evne) {
        return Reg.item("rune_" + evne.navn, p -> new RuneItem(p, evne),
                new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant());
    }

    public static final Item RUNE_SKYGGESPRANG = rune(RuneItem.Evne.SKYGGESPRANG);
    public static final Item RUNE_SJELESKJOLD = rune(RuneItem.Evne.SJELESKJOLD);
    public static final Item RUNE_DODSNOVA = rune(RuneItem.Evne.DODSNOVA);
    public static final Item RUNE_BLODHOST = rune(RuneItem.Evne.BLODHOST);
    public static final Item RUNE_ANDESPRANG = rune(RuneItem.Evne.ANDESPRANG);
    public static final Item RUNE_VOKTERKALL = rune(RuneItem.Evne.VOKTERKALL);

    public static final Item VAKT_SPAWN_EGG = Reg.item("vakt_spawn_egg", SpawnEggItem::new,
            new Item.Properties().spawnEgg(ModEntiteter.VAKT));

    // ------------------------------------------------------------ egen fane i kreativ-menyen
    public static final ResourceKey<CreativeModeTab> FANE = ResourceKey.create(Registries.CREATIVE_MODE_TAB, Reg.id("dodsfjellet"));

    public static void register() {
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, FANE, FabricCreativeModeTab.builder()
                .title(Component.translatable("itemGroup.dodsfjellet"))
                .icon(() -> new ItemStack(SJELESIGD))
                .displayItems((params, ut) -> {
                    for (Item i : new Item[]{BIBEL, PISTOL, HAGLE, AUTOMATGEVAER, SNIKSKYTTERGEVAER, KULER, HAGLPATRONER,
                            SJELESIGD, DODSKLINGE, VOKTERKNUSER, SKYGGEDOLK,
                            SJELEPLATE_HJELM, SJELEPLATE_BRYNJE, SJELEPLATE_BUKSER, SJELEPLATE_STOVLER,
                            FJELLVOKTER_HJELM, FJELLVOKTER_BRYNJE, FJELLVOKTER_BUKSER, FJELLVOKTER_STOVLER,
                            RUNE_SKYGGESPRANG, RUNE_SJELESKJOLD, RUNE_DODSNOVA, RUNE_BLODHOST, RUNE_ANDESPRANG, RUNE_VOKTERKALL,
                            DODSKRYSTALL, DODSNOKKEL, REISEKOMPASS, VAKT_SPAWN_EGG}) {
                        ut.accept(i);
                    }
                    for (var b : new net.minecraft.world.level.block.Block[]{ModBlokker.LYSKORS, ModBlokker.OPPGRADERINGSSMIE, ModBlokker.DODSSTEIN,
                            ModBlokker.DODSSTEIN_MURSTEIN, ModBlokker.POLERT_DODSSTEIN, ModBlokker.ASKEJORD, ModBlokker.BLODMOSE,
                            ModBlokker.DODSVED_STAMME, ModBlokker.DODSVED_PLANKER, ModBlokker.SJELEGLOD, ModBlokker.DODSKRYSTALL_MALM}) {
                        ut.accept(b);
                    }
                }).build());
    }
}
