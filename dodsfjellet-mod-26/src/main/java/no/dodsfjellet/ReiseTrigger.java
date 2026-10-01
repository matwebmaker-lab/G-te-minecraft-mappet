package no.dodsfjellet;

import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.permissions.LevelBasedPermissionSet;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.scores.Objective;
import net.minecraft.world.scores.ReadOnlyScoreInfo;
import net.minecraft.world.scores.Scoreboard;
import net.minecraft.world.scores.criteria.ObjectiveCriteria;

/**
 * Reisemenyen virker for ALLE spillere (ikke bare op): menyen klikker /trigger df_reise set N,
 * og modden leser verdien og teleporterer. Holder også riktig spillmodus per dimensjon:
 * Dødsfjellet-kartet = eventyr, Dødsriket og PvP-øya = overlevelse (der kan du bygge og bryte).
 */
public final class ReiseTrigger {
    private ReiseTrigger() {}

    public static final String OBJEKTIV = "df_reise";

    /** PvP-stasjonene (bygges av pvp-datapakken i verdenen på disse koordinatene). */
    public static final double[][] PVP = {
            {0.5, 101, 0.5, 0},      // 3 hub
            {100.5, 101, -12.5, 0},  // 4 duell
            {200.5, 101, -10.5, 0},  // 5 bot-trening
            {300.5, 101, 0.5, -90},  // 6 buetrening
            {400.5, 101, 0.5, -90},  // 7 bridge
            {500.5, 181, 0.5, 0},    // 8 MLG-tårnet (toppen)
            {600.5, 101, 0.5, -90},  // 9 parkour
            {700.5, 101, 0.5, 0},    // 10 alle mot alle
    };

    public static void register() {
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 5 != 0) return;
            Objective obj = objektiv(server);
            Scoreboard sb = server.getScoreboard();
            for (ServerPlayer p : server.getPlayerList().getPlayers()) {
                var tilgang = sb.getOrCreatePlayerScore(p, obj);
                if (tilgang.locked()) tilgang.unlock();
                ReadOnlyScoreInfo info = sb.getPlayerScoreInfo(p, obj);
                int valg = info == null ? 0 : info.value();
                if (valg != 0) {
                    tilgang.set(0);
                    utfor(p, valg);
                }
                spillmodus(p);
            }
        });
        // Dør du på PvP-øya, havner du tilbake på huben der i stedet for ved Dødsfjellet.
        ServerPlayerEvents.AFTER_RESPAWN.register((gammel, ny, iLive) -> {
            if (!iLive && gammel.level().dimension().equals(Reise.PVP)) {
                tilPvp(ny, PVP[0]);
            } else if (ny.level().dimension().equals(net.minecraft.world.level.Level.OVERWORLD) && ny.getY() < 0) {
                Reise.tilSpawn(ny);   // ingen seng: ikke la spilleren gjenoppstå inne i berget
            }
        });
    }

    private static Objective objektiv(MinecraftServer server) {
        Scoreboard sb = server.getScoreboard();
        Objective o = sb.getObjective(OBJEKTIV);
        if (o == null) {
            o = sb.addObjective(OBJEKTIV, ObjectiveCriteria.TRIGGER, Component.literal("Reise"),
                    ObjectiveCriteria.RenderType.INTEGER, false, null);
        }
        return o;
    }

    private static void utfor(ServerPlayer p, int valg) {
        switch (valg) {
            case 1 -> Reise.tilOververden(p);
            case 2 -> Reise.tilDodsriket(p);
            case 11 -> finnLandsby(p);
            default -> {
                if (valg >= 3 && valg <= 10) tilPvp(p, PVP[valg - 3]);
                else Reise.visMeny(p);
            }
        }
    }

    static void tilPvp(ServerPlayer p, double[] mal) {
        ServerLevel pvp = p.level().getServer().getLevel(Reise.PVP);
        if (pvp == null) return;
        p.teleport(new TeleportTransition(pvp, new Vec3(mal[0], mal[1], mal[2]), Vec3.ZERO, (float) mal[3], 0,
                TeleportTransition.PLAY_PORTAL_SOUND));
    }

    private static void finnLandsby(ServerPlayer p) {
        ServerLevel riket = p.level().getServer().getLevel(Reise.DODSRIKET);
        if (riket == null) return;
        if (!p.level().dimension().equals(Reise.DODSRIKET)) {
            p.sendSystemMessage(Component.literal("Du må være i Dødsriket for å lete etter Dødslandsbyen.").withStyle(ChatFormatting.RED));
            return;
        }
        CommandSourceStack kilde = p.createCommandSourceStack().withPermission(LevelBasedPermissionSet.OWNER);
        p.level().getServer().getCommands().performPrefixedCommand(kilde, "locate structure dodsfjellet:dodslandsbyen");
    }

    /** Eventyr i Dødsfjellet (ingen graving rundt fellene), overlevelse i Dødsriket og på PvP-øya. */
    private static void spillmodus(ServerPlayer p) {
        GameType naa = p.gameMode();
        if (naa == GameType.CREATIVE || naa == GameType.SPECTATOR) return;
        boolean eventyr = p.level().dimension().equals(net.minecraft.world.level.Level.OVERWORLD);
        GameType onsket = eventyr ? GameType.ADVENTURE : GameType.SURVIVAL;
        if (naa != onsket) p.setGameMode(onsket);
    }
}
