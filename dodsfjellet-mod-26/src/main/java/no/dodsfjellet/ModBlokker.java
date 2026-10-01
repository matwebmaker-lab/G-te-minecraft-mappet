package no.dodsfjellet;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.material.MapColor;

/** Blokkene i Dødsriket – alle med egne teksturer. */
public final class ModBlokker {
    private ModBlokker() {}

    private static BlockBehaviour.Properties stein(float hardhet) {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).instrument(NoteBlockInstrument.BASEDRUM)
                .requiresCorrectToolForDrops().strength(hardhet, 6.0f).sound(SoundType.DEEPSLATE);
    }

    public static final Block DODSSTEIN = Reg.blokk("dodsstein", Block::new, stein(2.0f));
    public static final Block DODSSTEIN_MURSTEIN = Reg.blokk("dodsstein_murstein", Block::new, stein(2.5f));
    public static final Block POLERT_DODSSTEIN = Reg.blokk("polert_dodsstein", Block::new, stein(2.5f));
    public static final Block ASKEJORD = Reg.blokk("askejord", Block::new, BlockBehaviour.Properties.of()
            .mapColor(MapColor.COLOR_GRAY).strength(0.6f).sound(SoundType.SOUL_SOIL));
    public static final Block BLODMOSE = Reg.blokk("blodmose", Block::new, BlockBehaviour.Properties.of()
            .mapColor(MapColor.CRIMSON_NYLIUM).strength(0.4f).sound(SoundType.NYLIUM)
            .lightLevel(s -> 3));
    public static final Block DODSVED_STAMME = Reg.blokk("dodsved_stamme", RotatedPillarBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(2.0f).sound(SoundType.WOOD)
                    .lightLevel(s -> 2));
    public static final Block DODSVED_PLANKER = Reg.blokk("dodsved_planker", Block::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(2.0f, 3.0f).sound(SoundType.WOOD));
    public static final Block SJELEGLOD = Reg.blokk("sjeleglod", Block::new, BlockBehaviour.Properties.of()
            .mapColor(MapColor.COLOR_LIGHT_BLUE).strength(0.4f).sound(SoundType.AMETHYST).lightLevel(s -> 15));
    public static final Block DODSKRYSTALL_MALM = Reg.blokk("dodskrystall_malm", Block::new,
            stein(3.0f).lightLevel(s -> 6));
    public static final Block OPPGRADERINGSSMIE = Reg.blokk("oppgraderingssmie", OppgraderingssmieBlock::new,
            stein(5.0f).lightLevel(s -> 10));

    public static void register() {
        // Feltene over registreres når klassen lastes.
    }
}
