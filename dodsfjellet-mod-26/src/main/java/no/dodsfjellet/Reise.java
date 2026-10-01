package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.Vec3;

/** Dimensjoner, ankomstplassen i Dødsriket og reisemenyen. */
public final class Reise {
    private Reise() {}

    public static final ResourceKey<Level> DODSRIKET = ResourceKey.create(Registries.DIMENSION, Reg.id("dodsriket"));
    public static final ResourceKey<Level> PVP = ResourceKey.create(Registries.DIMENSION, Reg.id("pvp"));

    /** Reisemeny-valg. Nummeret er verdien til /trigger df_reise som datapacken i verdenen håndterer. */
    public static final String[][] MENY = {
            {"1", "Dødsfjellet", "Inngangen til fangehullet"},
            {"2", "Dødsriket", "Ankomstplassen i den nye dimensjonen"},
            {"11", "Finn Dødslandsbyen", "Viser koordinatene til nærmeste Dødslandsby"},
            {"3", "PvP-øya", "Øvingsverdenen"},
            {"4", "Duell-arena", "1 mot 1 med kits"},
            {"5", "Bot-trening", "Slåss mot vakter på tre vanskelighetsgrader"},
            {"6", "Buetrening", "Skyt blinkene"},
            {"7", "Bridge-bane", "Bygg deg over tomrommet"},
            {"8", "MLG-tårnet", "Vannbøtte-hopp"},
            {"9", "Parkour", "Hoppebane"},
            {"10", "Alle mot alle", "Fri kamp med kit"},
    };

    public static void visMeny(ServerPlayer p) {
        p.sendSystemMessage(Component.literal("━━━━━━ REISEMENY ━━━━━━").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD));
        for (String[] valg : MENY) {
            MutableComponent linje = Component.literal("  ➤ " + valg[1]).withStyle(s -> s
                    .withColor(ChatFormatting.LIGHT_PURPLE)
                    .withClickEvent(new ClickEvent.RunCommand("/trigger df_reise set " + valg[0]))
                    .withHoverEvent(new HoverEvent.ShowText(Component.literal(valg[2]))));
            p.sendSystemMessage(linje);
        }
        p.sendSystemMessage(Component.literal("Klikk på et sted for å reise dit.").withStyle(ChatFormatting.GRAY));
    }

    /** Teleporterer spilleren til ankomstplassen i Dødsriket, og bygger den første gang. */
    public static void tilDodsriket(ServerPlayer p) {
        ServerLevel riket = p.level().getServer().getLevel(DODSRIKET);
        if (riket == null) {
            p.sendSystemMessage(Component.literal("Dødsriket finnes ikke i denne verdenen.").withStyle(ChatFormatting.RED));
            return;
        }
        BlockPos gulv = finnAnkomst(riket);
        if (!riket.getBlockState(gulv).is(ModBlokker.POLERT_DODSSTEIN)) {
            byggAnkomst(riket, gulv);
        }
        p.teleport(new TeleportTransition(riket, Vec3.atBottomCenterOf(gulv.above()), Vec3.ZERO, 0, 0,
                TeleportTransition.PLAY_PORTAL_SOUND));
        p.sendSystemMessage(Component.literal("Velkommen til Dødsriket...").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
    }

    private static BlockPos ankomst;

    /** Finner nærmeste faste land rundt (0,0) – Dødsriket har lavahav – og husker stedet. */
    private static BlockPos finnAnkomst(ServerLevel l) {
        if (ankomst != null && l.getBlockState(ankomst).is(ModBlokker.POLERT_DODSSTEIN)) return ankomst;
        for (int r = 0; r <= 320; r += 16) {
            for (int i = 0; i < Math.max(1, r / 4); i++) {
                double v = 2 * Math.PI * i / Math.max(1, r / 4);
                int x = (int) Math.round(Math.cos(v) * r), z = (int) Math.round(Math.sin(v) * r);
                l.getChunk(x >> 4, z >> 4);
                int y = l.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
                BlockPos p = new BlockPos(x, y - 1, z);
                if (l.getBlockState(p).is(ModBlokker.POLERT_DODSSTEIN)) return ankomst = p;
                if (l.getFluidState(p).isEmpty() && y > l.getSeaLevel() + 3 && y < 140 && torrtRundt(l, x, z)) return ankomst = p;
            }
        }
        l.getChunk(0, 0);
        return ankomst = new BlockPos(0, l.getHeight(Heightmap.Types.MOTION_BLOCKING, 0, 0) - 1, 0);
    }

    /** Ingen lava i en ring på 8 blokker rundt stedet. */
    private static boolean torrtRundt(ServerLevel l, int x, int z) {
        for (int[] d : new int[][]{{8, 0}, {-8, 0}, {0, 8}, {0, -8}, {6, 6}, {-6, 6}, {6, -6}, {-6, -6}}) {
            int y = l.getHeight(Heightmap.Types.MOTION_BLOCKING, x + d[0], z + d[1]);
            if (!l.getFluidState(new BlockPos(x + d[0], y - 1, z + d[1])).isEmpty()) return false;
        }
        return true;
    }

    private static void byggAnkomst(ServerLevel l, BlockPos gulv) {
        for (int dx = -5; dx <= 5; dx++) {
            for (int dz = -5; dz <= 5; dz++) {
                l.setBlockAndUpdate(gulv.offset(dx, 0, dz), (Math.abs(dx) == 5 || Math.abs(dz) == 5)
                        ? ModBlokker.DODSSTEIN_MURSTEIN.defaultBlockState() : ModBlokker.POLERT_DODSSTEIN.defaultBlockState());
                for (int dy = 1; dy <= 5; dy++) l.setBlockAndUpdate(gulv.offset(dx, dy, dz), Blocks.AIR.defaultBlockState());
            }
        }
        for (int[] h : new int[][]{{-5, -5}, {5, -5}, {-5, 5}, {5, 5}}) {
            l.setBlockAndUpdate(gulv.offset(h[0], 1, h[1]), ModBlokker.DODSSTEIN_MURSTEIN.defaultBlockState());
            l.setBlockAndUpdate(gulv.offset(h[0], 2, h[1]), ModBlokker.SJELEGLOD.defaultBlockState());
        }
        l.setBlockAndUpdate(gulv.offset(0, 1, -3), ModBlokker.OPPGRADERINGSSMIE.defaultBlockState());
    }

    /** Setter spilleren på bakken over verdens spawnpunkt (laster chunken først). */
    public static void tilSpawn(ServerPlayer p) {
        ServerLevel over = p.level().getServer().overworld();
        BlockPos spawn = over.getRespawnData().pos();
        over.getChunk(spawn.getX() >> 4, spawn.getZ() >> 4);
        int y = over.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, spawn.getX(), spawn.getZ());
        p.teleport(new TeleportTransition(over, new Vec3(spawn.getX() + 0.5, Math.max(y, spawn.getY()), spawn.getZ() + 0.5),
                Vec3.ZERO, over.getRespawnData().yaw(), 0, TeleportTransition.DO_NOTHING));
    }

    public static void tilOververden(ServerPlayer p) {
        ServerLevel over = p.level().getServer().overworld();
        p.teleport(new TeleportTransition(over, new Vec3(-893.5, 128, 452.5), Vec3.ZERO, -90, 0,
                TeleportTransition.PLAY_PORTAL_SOUND));
    }
}
