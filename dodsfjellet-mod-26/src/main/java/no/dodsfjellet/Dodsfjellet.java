package no.dodsfjellet;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.commands.Commands;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class Dodsfjellet implements ModInitializer {
    public static final String MOD_ID = "dodsfjellet";

    private static final EquipmentSlot[] RUSTNINGSPLASSER = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
    private static final Map<UUID, Integer> SLAGTELLER = new HashMap<>();
    private static final Map<UUID, Long> UDODELIG_NEDKJOLING = new HashMap<>();

    @Override
    public void onInitialize() {
        ModBlokker.register();
        ModEntiteter.register();
        ModGjenstander.register();
        ReiseTrigger.register();

        // /reise viser reisemenyen for alle spillere
        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, miljo) ->
                dispatcher.register(Commands.literal("reise").executes(ctx -> {
                    Reise.visMeny(ctx.getSource().getPlayerOrException());
                    return 1;
                })));

        // Nye spillere får et reisekompass
        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> {
            ServerPlayer p = handler.getPlayer();
            if (!p.entityTags().contains("df_kompass")) {
                // 26.x laster ikke spawn-chunkene på forhånd: nye spillere kan havne under bakken. Sett dem trygt på spawn.
                Reise.tilSpawn(p);
            }
            if (p.addTag("df_kompass")) {
                p.getInventory().add(new ItemStack(ModGjenstander.REISEKOMPASS));
                p.sendSystemMessage(Component.literal("Du fikk et Reisekompass! Høyreklikk det (eller skriv /reise) for å reise.")
                        .withStyle(ChatFormatting.LIGHT_PURPLE));
            }
        });

        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 20 != 0) return;
            for (ServerPlayer p : server.getPlayerList().getPlayers()) passiveEvner(p);
        });

        // Livstyveri (Blodhøst og våpen +5) og Dødsstøt (våpen +10)
        ServerLivingEntityEvents.AFTER_DAMAGE.register((offer, kilde, grunnSkade, skade, blokkert) -> {
            if (blokkert || skade <= 0 || !(kilde.getEntity() instanceof LivingEntity angriper) || angriper == offer) return;
            if (!(offer.level() instanceof ServerLevel sl)) return;
            float heling = 0;
            if (angriper.hasEffect(ModGjenstander.BLODHOST)) heling += skade * 0.4f;
            int vaapenNivaa = OppgraderingssmieBlock.nivaa(angriper.getMainHandItem());
            if (vaapenNivaa >= 5) heling += skade * 0.15f;
            if (heling > 0) angriper.heal(heling);
            if (vaapenNivaa >= 10 && kilde.getDirectEntity() == angriper) {
                int n = SLAGTELLER.merge(angriper.getUUID(), 1, Integer::sum);
                if (n % 4 == 0) {
                    offer.setInvulnerableTime(0);
                    offer.hurtServer(sl, sl.damageSources().indirectMagic(angriper, angriper), 6.0f);
                    offer.addEffect(new MobEffectInstance(MobEffects.WITHER, 80, 1));
                    sl.sendParticles(ParticleTypes.SCULK_SOUL, offer.getX(), offer.getY() + 1, offer.getZ(), 20, 0.4, 0.6, 0.4, 0.05);
                    sl.playSound(null, offer.blockPosition(), SoundEvents.WARDEN_ATTACK_IMPACT, SoundSource.PLAYERS, 1.0f, 0.7f);
                }
            }
        });

        // Udødelighet: full rustning med sum +40 redder deg fra døden én gang hvert 5. minutt
        ServerLivingEntityEvents.ALLOW_DEATH.register((offer, kilde, skade) -> {
            if (!(offer instanceof ServerPlayer p) || rustningSum(p) < 40) return true;
            long naa = p.level().getGameTime();
            Long sist = UDODELIG_NEDKJOLING.get(p.getUUID());
            if (sist != null && naa - sist < 6000) return true;
            UDODELIG_NEDKJOLING.put(p.getUUID(), naa);
            p.setHealth(8.0f);
            p.removeAllEffects();
            p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 200, 2));
            p.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 200, 2));
            p.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 400, 0));
            if (p.level() instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, p.getX(), p.getY() + 1, p.getZ(), 60, 0.5, 1.0, 0.5, 0.5);
                sl.playSound(null, p.blockPosition(), SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 1.0f, 0.8f);
            }
            p.sendOverlayMessage(Component.literal("Udødelighet reddet deg fra døden!").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
            return false;
        });
    }

    private static void passiveEvner(ServerPlayer p) {
        if (harSett(p, ModGjenstander.FJELLVOKTER_HJELM, ModGjenstander.FJELLVOKTER_BRYNJE,
                ModGjenstander.FJELLVOKTER_BUKSER, ModGjenstander.FJELLVOKTER_STOVLER)) {
            effekt(p, new MobEffectInstance(MobEffects.STRENGTH, 60, 0, true, false, true));
            effekt(p, new MobEffectInstance(MobEffects.RESISTANCE, 60, 0, true, false, true));
            effekt(p, new MobEffectInstance(MobEffects.NIGHT_VISION, 260, 0, true, false, true));
        }
        if (harSett(p, ModGjenstander.SJELEPLATE_HJELM, ModGjenstander.SJELEPLATE_BRYNJE,
                ModGjenstander.SJELEPLATE_BUKSER, ModGjenstander.SJELEPLATE_STOVLER)) {
            effekt(p, new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 60, 0, true, false, true));
            effekt(p, new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, false, true));
            effekt(p, new MobEffectInstance(MobEffects.JUMP_BOOST, 60, 1, true, false, true));
        }
        int sum = rustningSum(p);
        if (sum >= 20) effekt(p, new MobEffectInstance(MobEffects.SPEED, 60, 0, true, false, true));
        if (sum >= 40) effekt(p, new MobEffectInstance(MobEffects.RESISTANCE, 60, 1, true, false, true));
    }

    private static void effekt(Player p, MobEffectInstance e) {
        p.addEffect(e);
    }

    private static boolean harSett(Player p, Item hjelm, Item brynje, Item bukser, Item stovler) {
        return p.getItemBySlot(EquipmentSlot.HEAD).is(hjelm) && p.getItemBySlot(EquipmentSlot.CHEST).is(brynje)
                && p.getItemBySlot(EquipmentSlot.LEGS).is(bukser) && p.getItemBySlot(EquipmentSlot.FEET).is(stovler);
    }

    static int rustningSum(Player p) {
        int sum = 0;
        for (EquipmentSlot s : RUSTNINGSPLASSER) {
            ItemStack st = p.getItemBySlot(s);
            sum += OppgraderingssmieBlock.nivaa(st);
        }
        return sum;
    }
}
