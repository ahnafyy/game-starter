using UnrealBuildTool;

public class GameStarter : ModuleRules
{
    public GameStarter(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "EnhancedInput",
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "GameplayAbilities",
            "GameplayTags",
            "GameplayTasks",
            "ModularGameplay",
        });
    }
}
