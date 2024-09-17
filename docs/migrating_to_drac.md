# Migrating to DRAC

DISCLAIMER

Working across multiple clusters (ex. Mila and DRAC) at the same time can quickly 
become quite complex, as you will have to manage your project dependencies very 
attentively. Different versions of the same libraries can have different secondary 
dependencies and their behavior can change.

While usually only true for major version changes (i.e. version X.2.1, where "X" is the number that changes), 
sometimes minor version changes (i.e. 2.X.0) can also introduce breaking changes, like 
function names changing, functions not working the same way or even being removed.

## Things to consider when migrating to DRAC

If your project has been initiated somewhere else, either on your own workstation 
or on the Mila cluster, chances are you are using the most recent (at the time of your 
project's creation) versions of your Python libraries.

The first things to consider are therefore : Are those versions available in DRAC's 
pre-built wheels, and do I need to use these pre-built versions?

Version differences also need to take into account. If downgrading a 
library to match the version available on DRAC requires drastic changes to your code 
because of breaking changes between those versions, it might be better off not 
using the DRAC version if you don't have the time to make these changes (or don't 
want to break your code in other environments outside DRAC)

[See the Environment Creation and Management for DRAC document](environment_creation_drac.md)
