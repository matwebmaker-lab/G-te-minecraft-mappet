package no.dodsfjellet;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;

import java.util.function.Function;

/** Små hjelpere for registrering i 26.3 (alle gjenstander og blokker må ha id satt før de lages). */
public final class Reg {
    private Reg() {}

    public static Identifier id(String sti) {
        return Identifier.fromNamespaceAndPath(Dodsfjellet.MOD_ID, sti);
    }

    public static ResourceKey<Item> itemKey(String navn) {
        return ResourceKey.create(Registries.ITEM, id(navn));
    }

    public static ResourceKey<Block> blockKey(String navn) {
        return ResourceKey.create(Registries.BLOCK, id(navn));
    }

    public static <T extends Item> T item(String navn, Function<Item.Properties, T> fabrikk, Item.Properties props) {
        ResourceKey<Item> key = itemKey(navn);
        return Registry.register(BuiltInRegistries.ITEM, key, fabrikk.apply(props.setId(key)));
    }

    public static Item item(String navn, Item.Properties props) {
        return item(navn, Item::new, props);
    }

    public static <T extends Block> T blokk(String navn, Function<BlockBehaviour.Properties, T> fabrikk,
                                          BlockBehaviour.Properties props) {
        ResourceKey<Block> key = blockKey(navn);
        T blokk = Registry.register(BuiltInRegistries.BLOCK, key, fabrikk.apply(props.setId(key)));
        ResourceKey<Item> itemKey = itemKey(navn);
        BlockItem bi = new BlockItem(blokk, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix());
        bi.registerBlocks(Item.BY_BLOCK, bi);
        Registry.register(BuiltInRegistries.ITEM, itemKey, bi);
        return blokk;
    }
}
