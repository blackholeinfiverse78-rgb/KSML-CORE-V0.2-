# Folder Rename Instructions

## Current Folder Name
`KSML-V1-Task-1-`

## Target Folder Name
`KSML-V0.2`

## Manual Rename Steps

1. Close all applications accessing the folder (IDE, terminals, file explorers)
2. Navigate to `f:\KSML\`
3. Right-click on `KSML-V1-Task-1-` folder
4. Select "Rename"
5. Change name to `KSML-V0.2`
6. Press Enter

## Alternative: Command Line (after closing all processes)

```cmd
cd f:\KSML
ren KSML-V1-Task-1- KSML-V0.2
```

## Verification

After renaming, verify the structure:
```cmd
cd f:\KSML\KSML-V0.2
dir
```

All files and folders should be intact.

## Note

The rename is blocked because the folder is currently in use by the IDE or other processes. Close all applications accessing the folder before renaming.