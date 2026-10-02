package no.dodsfjellet;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/**
 * Bibelen: høyreklikk leser et vers (1930-oversettelsen) og gir Glede til deg og alle i nærheten.
 * Glede er noe man deler!
 */
public class BibelItem extends Item {
    static final String[][] VERS = {
            {"Herren er min hyrde, meg skal intet fattes.", "Salme 23,1"},
            {"Gled eder i Herren alltid! Atter vil jeg si: Gled eder!", "Filipperne 4,4"},
            {"Jeg er verdens lys; den som følger mig, skal ikke vandre i mørket.", "Johannes 8,12"},
            {"Alt makter jeg i ham som gjør mig sterk.", "Filipperne 4,13"},
            {"Vær sterk og modig! For Herren din Gud er med dig overalt hvor du går.", "Josva 1,9"},
            {"Kjærligheten er langmodig, kjærligheten er velvillig.", "1. Korinter 13,4"},
            {"For så har Gud elsket verden at han gav sin Sønn, den enbårne.", "Johannes 3,16"},
            {"Dette er dagen som Herren har gjort; la oss fryde oss og glede oss på den!", "Salme 118,24"},
            {"Kast all eders bekymring på ham! for han har omsorg for eder.", "1. Peter 5,7"},
            {"Herren velsigne dig og bevare dig!", "4. Mosebok 6,24"},
            {"Elsk din neste som dig selv.", "Matteus 22,39"},
            {"Ditt ord er en lykte for min fot og et lys på min sti.", "Salme 119,105"},
    };
    static final int NEDKJOLING = 1200;   // ett minutt

    public BibelItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player p, InteractionHand hand) {
        if (level instanceof ServerLevel sl) {
            String[] v = VERS[sl.getRandom().nextInt(VERS.length)];
            Component vers = Component.literal("✝ «" + v[0] + "»").withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC)
                    .append(Component.literal("  – " + v[1]).withStyle(ChatFormatting.YELLOW));
            for (Player venn : sl.getEntitiesOfClass(Player.class, p.getBoundingBox().inflate(12))) {
                venn.sendSystemMessage(vers);
                venn.addEffect(new MobEffectInstance(ModGjenstander.GLEDE, 600, 0));
                venn.addEffect(new MobEffectInstance(MobEffects.SPEED, 600, 0));
                sl.sendParticles(ParticleTypes.END_ROD, venn.getX(), venn.getY() + 2.2, venn.getZ(), 12, 0.4, 0.3, 0.4, 0.02);
            }
            sl.playSound(null, p.getX(), p.getY(), p.getZ(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1.2f, 1.2f);
            sl.playSound(null, p.getX(), p.getY(), p.getZ(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1.0f, 1.0f);
            p.getCooldowns().addCooldown(p.getItemInHand(hand), NEDKJOLING);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    @SuppressWarnings("deprecation")
    public void appendHoverText(ItemStack s, TooltipContext c, TooltipDisplay d, Consumer<Component> ut, TooltipFlag f) {
        ut.accept(Component.literal("Høyreklikk: les et vers").withStyle(ChatFormatting.GRAY));
        ut.accept(Component.literal("Gir Glede til deg og alle rundt deg").withStyle(ChatFormatting.YELLOW));
    }
}
