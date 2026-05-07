using UnrealBuildTool;
using System.Collections.Generic;

public class GameStarterTarget : TargetRules
{
    public GameStarterTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("GameStarter");
    }
}
