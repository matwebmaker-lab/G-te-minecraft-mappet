package no.dodsfjellet;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.sounds.SoundEvent;

/** Gevær-lydene (syntetisert av verktoy/lyder.py, se assets/dodsfjellet/sounds.json). */
public final class ModLyder {
    private ModLyder() {}

    private static SoundEvent lyd(String navn) {
        var id = Reg.id("gevaer." + navn);
        return Registry.register(BuiltInRegistries.SOUND_EVENT, id, SoundEvent.createVariableRangeEvent(id));
    }

    public static final SoundEvent PISTOL = lyd("pistol_skudd");
    public static final SoundEvent HAGLE = lyd("hagle_skudd");
    public static final SoundEvent AUTOMATGEVAER = lyd("automatgevaer_skudd");
    public static final SoundEvent SNIKSKYTTERGEVAER = lyd("snikskyttergevaer_skudd");
    public static final SoundEvent TOM = lyd("tom");
    public static final SoundEvent OMLAD_PISTOL = lyd("omlad_pistol");
    public static final SoundEvent OMLAD_AUTOMAT = lyd("omlad_automat");
    public static final SoundEvent OMLAD_HAGLE = lyd("omlad_hagle");
    public static final SoundEvent OMLAD_SNIKSKYTTER = lyd("omlad_snikskytter");
    public static final SoundEvent PUMPE = lyd("pumpe");

    public static void register() {}
}
