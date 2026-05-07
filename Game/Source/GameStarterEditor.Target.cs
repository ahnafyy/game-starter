using UnrealBuildTool;
using System.Collections.Generic;

public class GameStarterEditorTarget : TargetRules
{
    public GameStarterEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        // Match the engine's UndefinedIdentifierWarningLevel to avoid build product conflict
        UndefinedIdentifierWarningLevel = WarningLevel.Error;
        ExtraModuleNames.Add("GameStarter");
    }
}
