from services.utils import find_in_list, find_in_list_by_field

image_models = [
    {
        "value": "ICantBelieveItsNotPhotography_seco.safetensors [4e7a3dfd]",
        "label": "ICantBelievItsNotPhotographySeco",
    },
    {
        "value": "v1-5-pruned-emaonly.safetensors [d7049739]",
        "label": "SDV1.5",
    },
    {
        "value": "3Guofeng3_v34.safetensors [50f420de]",
        "label": "3Guofeng3 V3.4",
    },
    {
        "value": "absolutereality_V16.safetensors [37db0fc3]",
        "label": "AbsoluteRealityV1.6",
    },
    {
        "value": "absolutereality_v181.safetensors [3d9d4d2b]",
        "label": "AbsoluteRealityV1.8.1",
    },
    {
        "value": "amIReal_V41.safetensors [0a8a2e61]",
        "label": "AmIRealV4.1",
    },
    {
        "value": "analog-diffusion-1.0.ckpt [9ca13f02]",
        "label": "AnalogV1",
    },
    {
        "value": "anythingv3_0-pruned.ckpt [2700c435]",
        "label": "AnythingV3",
    },
    {
        "value": "anything-v4.5-pruned.ckpt [65745d25]",
        "label": "AnythingV4.5",
    },
    {
        "value": "anythingV5_PrtRE.safetensors [893e49b9]",
        "label": "AnythingV5",
    },
    {
        "value": "AOM3A3_orangemixs.safetensors [9600da17]",
        "label": "AbyssOrangeMixV3",
    },
    {
        "value": "blazing_drive_v10g.safetensors [ca1c1eab]",
        "label": "BlazingDriveV10g",
    },
    {
        "value": "breakdomain_I2428.safetensors [43cc7d2f]",
        "label": "BreakDomainI2428",
    },
    {
        "value": "breakdomain_M2150.safetensors [15f7afca]",
        "label": "BreakDomainM2150",
    },
    {
        "value": "cetusMix_Version35.safetensors [de2f2560]",
        "label": "CetusMixVersion35",
    },
    {
        "value": "childrensStories_v13D.safetensors [9dfaabcb]",
        "label": "ChildrenStoriesV13D",
    },
    {
        "value": "childrensStories_v1SemiReal.safetensors [a1c56dbb]",
        "label": "ChildrenStoriesV1SemiReal",
    },
    {
        "value": "childrensStories_v1ToonAnime.safetensors [2ec7b88b]",
        "label": "ChildrenStoriesV1Toon-Anime",
    },
    {
        "value": "Counterfeit_v30.safetensors [9e2a8f19]",
        "label": "CounterfeitV3.0",
    },
    {
        "value": "cuteyukimixAdorable_midchapter3.safetensors [04bdffe6]",
        "label": "CuteYukimixMidChapter3",
    },
    {
        "value": "cyberrealistic_v33.safetensors [82b0d085]",
        "label": "CyberRealisticV3.3",
    },
    {
        "value": "dalcefo_v4.safetensors [425952fe]",
        "label": "DalcefoV4",
    },
    {
        "value": "deliberate_v2.safetensors [10ec4b29]",
        "label": "DeliberateV2",
    },
    {
        "value": "deliberate_v3.safetensors [afd9d2d4]",
        "label": "DeliberateV3",
    },
    {
        "value": "dreamlike-anime-1.0.safetensors [4520e090]",
        "label": "DreamlikeAnime V1",
    },
    {
        "value": "dreamlike-diffusion-1.0.safetensors [5c9fd6e0]",
        "label": "DreamlikeDiffusionV1",
    },
    {
        "value": "dreamlike-photoreal-2.0.safetensors [fdcf65e7]",
        "label": "DreamlikePhotorealV2",
    },
    {
        "value": "dreamshaper_6BakedVae.safetensors [114c8abb]",
        "label": "Dreamshaper6baked vae",
    },
    {
        "value": "dreamshaper_7.safetensors [5cf5ae06]",
        "label": "Dreamshaper7",
    },
    {
        "value": "dreamshaper_8.safetensors [9d40847d]",
        "label": "Dreamshaper8",
    },
    {
        "value": "edgeOfRealism_eorV20.safetensors [3ed5de15]",
        "label": "EdgeofRealismEORV2.0",
    },
    {
        "value": "EimisAnimeDiffusion_V1.ckpt [4f828a15]",
        "label": "EimisAnimeDiffusionV1.0",
    },
    {
        "value": "elldreths-vivid-mix.safetensors [342d9d26]",
        "label": "ElldrethVivid",
    },
    {
        "value": "epicphotogasm_xPlusPlus.safetensors [1a8f6d35]",
        "label": "epiCPhotoGasmXPlusPlus",
    },
    {
        "value": "epicrealism_naturalSinRC1VAE.safetensors [90a4c676]",
        "label": "EpiCRealismNaturalSinRC1",
    },
    {
        "value": "epicrealism_pureEvolutionV3.safetensors [42c8440c]",
        "label": "EpiCRealismPureEvolutionV3",
    },

    {
        "value": "indigoFurryMix_v75Hybrid.safetensors [91208cbb]",
        "label": "IndigoFurryMixV7.5Hybrid",
    },
    {
        "value": "juggernaut_aftermath.safetensors [5e20c455]",
        "label": "JuggernautAftermath",
    },
    {
        "value": "lofi_v4.safetensors [ccc204d6]",
        "label": "LofiV4",
    },
    {
        "value": "lyriel_v16.safetensors [68fceea2]",
        "label": "LyrielV1.6",
    },
    {
        "value": "majicmixRealistic_v4.safetensors [29d0de58]",
        "label": "MajicMixRealistic V4",
    },
    {
        "value": "mechamix_v10.safetensors [ee685731]",
        "label": "MechaMixV1.0",
    },
    {
        "value": "meinamix_meinaV9.safetensors [2ec66ab0]",
        "label": "MeinaMixMeina V9",
    },
    {
        "value": "meinamix_meinaV11.safetensors [b56ce717]",
        "label": "MeinaMixMeina V11",
    },
    {
        "value": "neverendingDream_v122.safetensors [f964ceeb]",
        "label": "NeverendingDream V1.22",
    },
    {
        "value": "openjourney_V4.ckpt [ca2f377f]",
        "label": "OpenjourneyV4",
    },
    {
        "value": "pastelMixStylizedAnime_pruned_fp16.safetensors [793a26e8]",
        "label": "Pastel-Mix",
    },
    {
        "value": "portraitplus_V1.0.safetensors [1400e684]",
        "label": "Portrait+V1",
    },
    {
        "value": "protogenx34.safetensors [5896f8d5]",
        "label": "Protogenx3.4",
    },
    {
        "value": "Realistic_Vision_V1.4-pruned-fp16.safetensors [8d21810b]",
        "label": "RealisticVisionV1.4",
    },
    {
        "value": "Realistic_Vision_V2.0.safetensors [79587710]",
        "label": "RealisticVisionV2.0",
    },
    {
        "value": "Realistic_Vision_V4.0.safetensors [29a7afaa]",
        "label": "RealisticVisionV4.0",
    },
    {
        "value": "Realistic_Vision_V5.0.safetensors [614d1063]",
        "label": "RealisticVisionV5.0",
    },
    {
        "value": "redshift_diffusion-V10.safetensors [1400e684]",
        "label": "RedshiftDiffusionV1.0",
    },
    {
        "value": "revAnimated_v122.safetensors [3f4fefd9]",
        "label": "ReVAnimatedV1.2.2",
    },
    {
        "value": "rundiffusionFX25D_v10.safetensors [cd12b0ee]",
        "label": "RunDiffusionFX2.5DV1.0",
    },
    {
        "value": "rundiffusionFX_v10.safetensors [cd4e694d]",
        "label": "RunDiffusionFXPhotorealistic V1.0",
    },
    {
        "value": "sdv1_4.ckpt [7460a6fa]",
        "label": "SDV1.4",
    },
    {
        "value": "v1-5-inpainting.safetensors [21c7ab71]",
        "label": "SDV1.5Inpainting",
    },
    {
        "value": "shoninsBeautiful_v10.safetensors [25d8c546]",
        "label": "ShoninBeautifulPeopleV1.0",
    },
    {
        "value": "theallys-mix-ii-churned.safetensors [5d9225a4]",
        "label": "TheAllyMixII",
    },
    {
        "value": "timeless-1.0.ckpt [7c4971d4]",
        "label": "TimelessV1",
    },
    {
        "value": "toonyou_beta6.safetensors [980f6b15]",
        "label": "ToonYouBeta6",
    }
]

samplers = [
    {
        "value": "Euler",
        "label": "Euler",
    },
    {
        "value": "Euler a",
        "label": "EulerA",
    },
    {
        "value": "Heun",
        "label": "Heun",
    },
    {
        "value": "DPM++ 2MKarras",
        "label": "DPM++2MKarras",
    },
    {
        "value": "DPM++ SDE Karras",
        "label": "DPM++SDEKarras",
    },
    {
        "value": "DDIM",
        "label": "DDIM",
    },
]

cgf_values = list(range(0, 22, 2))
steps_values = list(range(0, 26, 2))
samplers_values = [sampler["label"] for sampler in samplers]
image_models_values = [image_model["label"] for image_model in image_models]


def get_image_model_by_value(label: str):
    return find_in_list_by_field(image_models, "value", label)


def get_image_model_by_label(label: str):
    return find_in_list_by_field(image_models, "label", label)


def get_samplers_by_value(label: str):
    return find_in_list_by_field(image_models, "value", label)


def get_samplers_by_label(label: str):
    return find_in_list_by_field(samplers, "label", label)
