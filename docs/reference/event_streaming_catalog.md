---
title: "Event-Only Telemetry Streaming Catalog"
tags: ["telemetry", "events", "streaming", "catalog", "unmapped", "reference"]
created_at: "2026-11-23"
last_updated_at: "2026-11-23"
---

# Event-Only Telemetry Streaming Catalog

> [!NOTE]
> Deterministically generated from **`ed-models` v0.2.1**. Catalogs all 520 telemetry properties available exclusively via asynchronous event streaming rather than state projections.

## How to Consume Event-Only Properties

Properties in this catalog are not held in long-lived state projections. Instead, applications subscribe directly to the event schemas that emit them using the client event dispatcher:

```python
from ed_models.core.domain.events import EjectCargo

@client.on(EjectCargo)
def on_cargo_ejected(event: EjectCargo) -> None:
    # Read event-only properties directly from the hydrated event
    is_abandoned = event.Abandoned
    cargo_type = event.Type
```

---

## 1. Tier 4: Granular, Ephemeral & Event-Specific Payload Data (520 Properties)

| Property | Primary Event | Fidelity | Fallback Events |
| :--- | :--- | :---: | :--- |
| `abandoned` | `EjectCargo` | 0.66 | — |
| `absolutemagnitude` | `ScanStar` | 0.75 | — |
| `active` | `Missions` | 0.61 | — |
| `activefine` | `Docked` | 0.66 | — |
| `added` | `BackpackChange` | 0.61 | — |
| `additional_fields` | `StatusTelemetry` | 0.91 | — |
| `age_my` | `ScanStar` | 0.75 | — |
| `allfines` | `PayBounties` | 0.61 | `PayFines` |
| `alliance` | `Reputation` | 0.70 | — |
| `allowcobramkiv` | `ExtendedShipyard` | 0.61 | — |
| `allownotorious` | `CarrierDockingPermission` | 0.66 | `CarrierStats` |
| `amount` | `CarrierDepositFuel` | 0.70 | `ColonisationContributionResource`, `NpcCrewPaidWage`, `PayBounties` *(+6 more)* |
| `applyexperimentaleffect` | `EngineerCraft` | 0.65 | `EngineerLegacyConvert` |
| `ascendingnode` | `ScanBaryCentre` | 0.75 | `ScanBody`, `ScanOther`, `ScanPlanet` *(+1 more)* |
| `atmosphere` | `ScanPlanet` | 0.69 | — |
| `atmospherecomposition` | `ScanPlanet` | 0.66 | — |
| `atmospheretype` | `ScanPlanet` | 0.69 | — |
| `availablebalance` | `CarrierFinance` | 0.70 | — |
| `avgpricepaid` | `MarketSell` | 0.73 | — |
| `awardingfaction` | `CapShipBond` | 0.65 | `FactionKillBond` |
| `awardingfaction_localised` | `CapShipBond` | 0.65 | `FactionKillBond` |
| `axialtilt` | `ScanBody` | 0.75 | `ScanOther`, `ScanPlanet`, `ScanStar` |
| `balance` | `Status` | 0.80 | — |
| `bank_account` | `Statistics` | 0.61 | — |
| `bankrupt` | `Resurrect` | 0.61 | — |
| `basevalue` | `MultiSellExplorationData` | 0.70 | `SellExplorationData` |
| `biodata` | `SellOrganicData` | 0.61 | — |
| `blackmarket` | `CarrierTradeOrder` | 0.66 | `MarketSell` |
| `blueprint` | `EngineerApply` | 0.65 | `EngineerCraft`, `EngineerLegacyConvert` |
| `blueprintid` | `EngineerCraft` | 0.73 | `EngineerLegacyConvert` |
| `blueprintname` | `EngineerCraft` | 0.65 | `EngineerLegacyConvert` |
| `bodies` | `DiscoveryScan` | 0.75 | — |
| `body_localised` | `Location` | 0.65 | — |
| `bodycount` | `FSSDiscoveryScan` | 0.75 | — |
| `bodyname` | `Status` | 0.73 | `SAAScanComplete`, `ScanBody`, `ScanOther` *(+5 more)* |
| `bonus` | `MultiSellExplorationData` | 0.70 | `SellExplorationData` |
| `boostused` | `FSDJump` | 0.75 | — |
| `boostvalue` | `JetConeBoost` | 0.70 | — |
| `boughtatmarket` | `CarrierBuy` | 0.70 | — |
| `bounty` | `CommitCrime` | 0.70 | `CrimeVictim`, `ShipTargeted` |
| `brokerpercentage` | `PayBounties` | 0.70 | `PayFines`, `PayLegacyFines`, `RedeemVoucher` |
| `brokertype` | `TechnologyBroker` | 0.65 | — |
| `build` | `Fileheader` | 0.65 | `LoadGame` |
| `bundleid` | `ShipyardRedeem` | 0.73 | — |
| `buyitem` | `ModuleBuy` | 0.65 | `ModuleBuyAndStore` |
| `buyitem_localised` | `ModuleBuy` | 0.65 | `ModuleBuyAndStore` |
| `buyprice` | `BuyDrones` | 0.70 | `MarketBuy`, `ModuleBuy`, `ModuleBuyAndStore` |
| `callsign` | `CarrierBuy` | 0.65 | `CarrierNameChange`, `CarrierStats` |
| `canceltrade` | `CarrierTradeOrder` | 0.66 | — |
| `captain` | `JoinACrew` | 0.65 | `QuitACrew` |
| `cargocapacity` | `Loadout` | 0.70 | — |
| `cargotype` | `CargoDepot` | 0.69 | — |
| `cargotype_localised` | `CargoDepot` | 0.69 | — |
| `carrierbalance` | `CarrierBankTransfer` | 0.70 | `CarrierFinance` |
| `carrierdockingaccess` | `Market` | 0.69 | `ExtendedMarket` |
| `carrierid` | `CarrierDockingPermission` | 0.78 | `CarrierJumpCancelled`, `CarrierTradeOrder`, `CarrierBankTransfer` *(+16 more)* |
| `carriername` | `ExtendedFCMaterials` | 0.65 | `FCMaterials` |
| `carriertype` | `CarrierDockingPermission` | 0.66 | `CarrierJumpCancelled`, `CarrierTradeOrder`, `CarrierBankTransfer` *(+13 more)* |
| `category` | `TradeMicroResources` | 0.69 | `CodexEntry`, `MaterialCollected`, `MaterialDiscarded` *(+3 more)* |
| `category_localised` | `CodexEntry` | 0.65 | — |
| `cgid` | `CommunityGoalDiscard` | 0.73 | `CommunityGoalJoin`, `CommunityGoalReward` |
| `channel` | `ReceiveText` | 0.69 | — |
| `class` | `BuyWeapon` | 0.70 | `LoadoutEquipModule`, `SellWeapon`, `UpgradeSuit` *(+1 more)* |
| `cockpitbreach` | `Docked` | 0.66 | — |
| `cockpitrepaired` | `RepairDrone` | 0.70 | — |
| `combat` | `Progress` | 0.70 | `Promotion`, `Rank`, `Statistics` |
| `combatrank` | `CrewHire` | 0.70 | `Interdicted`, `Interdiction`, `PVPKill` |
| `commodities` | `TechnologyBroker` | 0.61 | — |
| `commodity` | `CarrierTradeOrder` | 0.69 | `EngineerContribution`, `MissionAccepted`, `MissionCompleted` |
| `commodity_localised` | `CarrierTradeOrder` | 0.69 | `EngineerContribution`, `MissionAccepted`, `MissionCompleted` |
| `commodityreward` | `MissionCompleted` | 0.61 | — |
| `complete` | `Missions` | 0.61 | — |
| `components` | `Backpack` | 0.61 | `ShipLocker` |
| `composition` | `ScanPlanet` | 0.66 | — |
| `conflicts` | `FSDJump` | 0.66 | `CarrierJump`, `Location` |
| `constructioncomplete` | `ColonisationConstructionDepot` | 0.61 | — |
| `constructionfailed` | `ColonisationConstructionDepot` | 0.61 | — |
| `constructionprogress` | `ColonisationConstructionDepot` | 0.70 | — |
| `consumables` | `Backpack` | 0.61 | `ShipLocker` |
| `content` | `ProspectedAsteroid` | 0.65 | — |
| `content_localised` | `ProspectedAsteroid` | 0.65 | — |
| `contributions` | `ColonisationContribution` | 0.61 | — |
| `controllingpower` | `FSDJump` | 0.69 | `CarrierJump`, `Location` |
| `corrosionrepaired` | `RepairDrone` | 0.70 | — |
| `cost` | `BuyTradeData` | 0.75 | `BookDropship`, `BookTaxi`, `BuyAmmo` *(+15 more)* |
| `count` | `Cargo` | 0.75 | `CargoDepot`, `EjectCargo`, `TradeMicroResources` *(+21 more)* |
| `cqc` | `Progress` | 0.70 | `Promotion`, `Rank`, `Statistics` |
| `crafting` | `Statistics` | 0.61 | — |
| `crew` | `CrewLaunchFighter` | 0.65 | `CrewMemberJoins`, `CrewMemberQuits`, `CrewMemberRoleChange` *(+4 more)* |
| `crewid` | `CrewAssign` | 0.73 | `CrewFire`, `CrewHire` |
| `crewname` | `CarrierCrewServices` | 0.65 | — |
| `crewrole` | `CarrierCrewServices` | 0.65 | — |
| `crime` | `Statistics` | 0.61 | — |
| `crimetype` | `CommitCrime` | 0.65 | `CrimeVictim` |
| `currentgoals` | `CommunityGoal` | 0.61 | — |
| `currentrank` | `SquadronStartup` | 0.60 | — |
| `currentrankname` | `SquadronStartup` | 0.55 | — |
| `currentrankname_localised` | `SquadronStartup` | 0.55 | — |
| `data` | `Backpack` | 0.61 | `ShipLocker` |
| `departuretime` | `CarrierJumpRequest` | 0.59 | — |
| `deposit` | `CarrierBankTransfer` | 0.70 | — |
| `destination` | `Status` | 0.70 | — |
| `destinationlocation` | `BookDropship` | 0.65 | `BookTaxi` |
| `destinationsettlement` | `MissionAccepted` | 0.65 | `MissionCompleted` |
| `destinationstation` | `MissionAccepted` | 0.65 | `MissionCompleted` |
| `destinationsystem` | `BookDropship` | 0.65 | `BookTaxi`, `MissionAccepted`, `MissionCompleted` |
| `discovered` | `SellExplorationData` | 0.65 | `MultiSellExplorationData` |
| `discoverynumber` | `MaterialDiscovered` | 0.70 | — |
| `distance` | `ShipyardTransfer` | 0.70 | — |
| `distancefromarrivalls` | `ScanBody` | 0.75 | `ScanOther`, `ScanPlanet`, `ScanStar` |
| `distfromstarls` | `Docked` | 0.75 | `Location` |
| `dockingaccess` | `CarrierDockingPermission` | 0.69 | `CarrierStats` |
| `donated` | `MissionCompleted` | 0.70 | — |
| `donation` | `MissionCompleted` | 0.70 | `MissionAccepted` |
| `eccentricity` | `ScanBaryCentre` | 0.75 | `ScanBody`, `ScanOther`, `ScanPlanet` *(+1 more)* |
| `efficiencytarget` | `SAAScanComplete` | 0.75 | — |
| `empire` | `Progress` | 0.70 | `Promotion`, `Rank`, `Reputation` |
| `encoded` | `Materials` | 0.61 | — |
| `endmarketid` | `CargoDepot` | 0.78 | — |
| `engineer` | `EngineerApply` | 0.65 | `EngineerBase`, `EngineerContribution`, `EngineerCraft` *(+3 more)* |
| `engineerid` | `EngineerBase` | 0.73 | `EngineerContribution`, `EngineerCraft`, `EngineerLegacyConvert` *(+2 more)* |
| `engineermodifications` | `ModuleRetrieve` | 0.65 | `ModuleStore` |
| `engineers` | `EngineerProgress` | 0.61 | — |
| `entryid` | `CodexEntry` | 0.73 | — |
| `event` | `Status` | 0.91 | `ApproachBody`, `BuyTradeData`, `Cargo` *(+282 more)* |
| `exobiologist` | `Progress` | 0.70 | `Promotion`, `Rank` |
| `exobiology` | `Statistics` | 0.61 | — |
| `experimentaleffect` | `EngineerCraft` | 0.65 | `EngineerLegacyConvert` |
| `experimentaleffect_localised` | `EngineerCraft` | 0.65 | `EngineerLegacyConvert` |
| `expires` | `Mission` | 0.70 | — |
| `expiry` | `MissionAccepted` | 0.65 | — |
| `exploration` | `Statistics` | 0.61 | — |
| `explore` | `Progress` | 0.70 | `Promotion`, `Rank` |
| `faction` | `Bounty` | 0.65 | `CommitCrime`, `CrewHire`, `EngineerContribution` *(+8 more)* |
| `faction_localised` | `Bounty` | 0.65 | `PayBounties`, `PayFines` |
| `factioneffects` | `MissionCompleted` | 0.61 | — |
| `factions` | `FSDJump` | 0.66 | `CarrierJump`, `Location`, `RedeemVoucher` |
| `failed` | `Missions` | 0.61 | — |
| `federation` | `Progress` | 0.70 | `Promotion`, `Rank`, `Reputation` |
| `fighter` | `HullDamage` | 0.61 | — |
| `filename` | `Screenshot` | 0.65 | — |
| `finance` | `CarrierStats` | 0.61 | — |
| `fine` | `CommitCrime` | 0.70 | `CrimeVictim`, `MissionAbandoned`, `MissionFailed` |
| `fleetcarrier` | `Statistics` | 0.61 | — |
| `from` | `ReceiveText` | 0.69 | — |
| `from_localised` | `ReceiveText` | 0.69 | — |
| `fromitem` | `ModuleSwap` | 0.65 | — |
| `fromitem_localised` | `ModuleSwap` | 0.65 | — |
| `frompower` | `PowerplayDefect` | 0.65 | — |
| `fromslot` | `ModuleSwap` | 0.65 | — |
| `fuelcapacity` | `LoadGame` | 0.70 | `Loadout` |
| `fuellevel` | `FSDJump` | 0.75 | `CarrierStats`, `LoadGame` |
| `fuelmain` | `ReservoirReplenished` | 0.70 | — |
| `fuelreservoir` | `ReservoirReplenished` | 0.70 | — |
| `fuelused` | `FSDJump` | 0.75 | — |
| `fullyrepaired` | `AfmuRepairs` | 0.61 | — |
| `gamemode` | `GameModeChange` | 0.82 | `LoadGame` |
| `gameversion` | `Fileheader` | 0.65 | `LoadGame` |
| `genus` | `ScanOrganic` | 0.69 | — |
| `genus_localised` | `ScanOrganic` | 0.69 | — |
| `genuses` | `SAASignalsFound` | 0.61 | — |
| `guifocus` | `Status` | 0.80 | — |
| `height` | `Screenshot` | 0.70 | — |
| `horizons` | `ExtendedOutfitting` | 0.61 | `ExtendedShipyard`, `LoadGame` |
| `hot` | `Loadout` | 0.61 | `ModuleRetrieve`, `ModuleStore` |
| `hullrepaired` | `RepairDrone` | 0.70 | — |
| `hullvalue` | `Loadout` | 0.70 | — |
| `id` | `DockFighter` | 0.78 | `DockSRV`, `Disembark`, `Embark` *(+6 more)* |
| `illegalgoods` | `MarketSell` | 0.61 | — |
| `independent` | `Reputation` | 0.70 | — |
| `influence` | `MissionAccepted` | 0.65 | — |
| `ingredients` | `EngineerCraft` | 0.61 | — |
| `innerrad` | `Ring` | 0.70 | — |
| `insrv` | `Location` | 0.61 | — |
| `interdicted` | `Interdiction` | 0.65 | — |
| `interdictor` | `EscapeInterdiction` | 0.65 | `Interdicted` |
| `interdictor_localised` | `EscapeInterdiction` | 0.65 | `Interdicted` |
| `inventory` | `Cargo` | 0.66 | — |
| `isnewentry` | `CodexEntry` | 0.61 | — |
| `isplayer` | `EscapeInterdiction` | 0.61 | `Interdicted`, `Interdiction` |
| `ispreview` | `EngineerLegacyConvert` | 0.61 | — |
| `isstation` | `FSSSignalDiscovered` | 0.61 | — |
| `item` | `Repair` | 0.65 | — |
| `item_localised` | `Repair` | 0.65 | — |
| `items` | `Repair` | 0.65 | `Backpack`, `ExtendedFCMaterials`, `ExtendedMarket` *(+4 more)* |
| `itemscollected` | `CargoDepot` | 0.75 | — |
| `itemsdelivered` | `CargoDepot` | 0.75 | — |
| `itemsunlocked` | `TechnologyBroker` | 0.61 | — |
| `jumpdist` | `FSDJump` | 0.75 | — |
| `jumprangecurr` | `CarrierStats` | 0.70 | — |
| `jumprangemax` | `CarrierStats` | 0.70 | — |
| `jumptype` | `StartJump` | 0.56 | — |
| `killcount` | `MissionAccepted` | 0.70 | `MissionCompleted` |
| `killername` | `Died` | 0.65 | — |
| `killername_localised` | `Died` | 0.65 | — |
| `killerrank` | `Died` | 0.65 | — |
| `killership` | `Died` | 0.65 | — |
| `landable` | `ScanPlanet` | 0.66 | — |
| `landingpad` | `DockingGranted` | 0.75 | — |
| `landingpads` | `Docked` | 0.66 | `DockingRequested` |
| `language` | `Fileheader` | 0.65 | `LoadGame` |
| `legalstate` | `Status` | 0.70 | — |
| `legalstatus` | `ShipTargeted` | 0.55 | — |
| `level` | `EngineerApply` | 0.70 | `EngineerCraft`, `EngineerLegacyConvert`, `ModuleRetrieve` *(+1 more)* |
| `loadout` | `FighterRebuilt` | 0.65 | `LaunchFighter`, `LaunchSRV`, `RestockVehicle` |
| `loadoutid` | `CreateSuitLoadout` | 0.73 | `DeleteSuitLoadout`, `LoadoutEquipModule`, `RenameSuitLoadout` *(+2 more)* |
| `loadoutname` | `CreateSuitLoadout` | 0.65 | `DeleteSuitLoadout`, `LoadoutEquipModule`, `RenameSuitLoadout` *(+2 more)* |
| `localisedname` | `MissionAbandoned` | 0.65 | `MissionAccepted`, `MissionCompleted`, `MissionFailed` *(+1 more)* |
| `location` | `CarrierBuy` | 0.65 | — |
| `luminosity` | `ScanStar` | 0.69 | — |
| `manifest` | `Passengers` | 0.61 | — |
| `manufactured` | `Materials` | 0.61 | — |
| `massem` | `ScanPlanet` | 0.75 | — |
| `massmt` | `Ring` | 0.70 | — |
| `material` | `EngineerContribution` | 0.65 | — |
| `material_localised` | `EngineerContribution` | 0.65 | — |
| `material_trader_stats` | `Statistics` | 0.61 | — |
| `materials` | `ScanPlanet` | 0.66 | `ProspectedAsteroid`, `Synthesis`, `TechnologyBroker` |
| `materialsreward` | `MissionCompleted` | 0.61 | — |
| `maxjumprange` | `Loadout` | 0.70 | — |
| `meananomaly` | `ScanBaryCentre` | 0.75 | `ScanBody`, `ScanOther`, `ScanPlanet` *(+1 more)* |
| `merits` | `Powerplay` | 0.70 | — |
| `meritsgained` | `PowerplayMerits` | 0.70 | — |
| `message` | `DatalinkScan` | 0.69 | `ReceiveText`, `SendText` |
| `message_localised` | `DatalinkScan` | 0.69 | `ReceiveText` |
| `microresources` | `DeliverPowerMicroResources` | 0.61 | `NewBuyMicroResources`, `SellMicroResources` |
| `mining` | `Statistics` | 0.61 | — |
| `missionid` | `CargoDepot` | 0.78 | `CollectCargo`, `BackpackItem`, `ChangedBackpackItem` *(+7 more)* |
| `modifiers` | `EngineerCraft` | 0.61 | `EngineerLegacyConvert` |
| `module` | `AfmuRepairs` | 0.65 | `EngineerCraft`, `EngineerLegacyConvert`, `JetConeDamage` |
| `module_localised` | `AfmuRepairs` | 0.65 | `JetConeDamage` |
| `modulename` | `LoadoutEquipModule` | 0.65 | — |
| `modulename_localised` | `LoadoutEquipModule` | 0.65 | — |
| `modulepacks` | `CarrierStats` | 0.61 | — |
| `modules` | `RebootRepair` | 0.65 | `CreateSuitLoadout`, `ExtendedModuleInfo`, `Loadout` *(+2 more)* |
| `modulesvalue` | `Loadout` | 0.70 | — |
| `motherlodematerial` | `ProspectedAsteroid` | 0.65 | — |
| `motherlodematerial_localised` | `ProspectedAsteroid` | 0.65 | — |
| `multicrew` | `Docked` | 0.66 | `FSDJump`, `Liftoff`, `SupercruiseEntry` *(+8 more)* |
| `musictrack` | `Music` | 0.69 | — |
| `name` | `ApproachSettlement` | 0.65 | `BackpackItem`, `BuySuit`, `BuyWeapon` *(+42 more)* |
| `name_localised` | `ApproachSettlement` | 0.65 | `BackpackItem`, `BuySuit`, `BuyWeapon` *(+19 more)* |
| `nearestdestination` | `Liftoff` | 0.69 | `Touchdown`, `CodexEntry` |
| `nearestdestination_localised` | `Liftoff` | 0.69 | `Touchdown`, `CodexEntry` |
| `newdestinationstation` | `MissionCompleted` | 0.65 | `MissionRedirected` |
| `newdestinationsystem` | `MissionCompleted` | 0.65 | `MissionRedirected` |
| `newrank` | `SquadronDemotion` | 0.70 | `SquadronPromotion` |
| `newrankname` | `SquadronDemotion` | 0.65 | `SquadronPromotion` |
| `newshipid` | `ShipRedeemed` | 0.73 | `ShipyardNew` |
| `newtraitsdiscovered` | `CodexEntry` | 0.61 | — |
| `nonbodycount` | `FSSDiscoveryScan` | 0.75 | — |
| `npccrewid` | `NpcCrewPaidWage` | 0.73 | `NpcCrewRank` |
| `npccrewname` | `NpcCrewPaidWage` | 0.65 | `NpcCrewRank` |
| `numbodies` | `NavBeaconScan` | 0.75 | — |
| `odyssey` | `Fileheader` | 0.61 | `LoadGame` |
| `offender` | `CrimeVictim` | 0.65 | — |
| `offered` | `TradeMicroResources` | 0.66 | — |
| `olddestinationstation` | `MissionRedirected` | 0.65 | — |
| `olddestinationsystem` | `MissionRedirected` | 0.65 | — |
| `oldrank` | `SquadronDemotion` | 0.70 | `SquadronPromotion` |
| `oldrankname` | `SquadronDemotion` | 0.65 | `SquadronPromotion` |
| `oncrime` | `EndCrewSession` | 0.61 | `KickCrewMember` |
| `onfoot` | `CarrierJump` | 0.61 | `Location` |
| `onplanet` | `Liftoff` | 0.66 | `Touchdown`, `Disembark`, `DropshipDeploy` *(+1 more)* |
| `onstation` | `Liftoff` | 0.66 | `Touchdown`, `Disembark`, `DropshipDeploy` *(+1 more)* |
| `operation` | `CarrierCrewServices` | 0.65 | `CarrierModulePackBuy`, `CarrierModulePackSell`, `CarrierShipPackBuy` *(+1 more)* |
| `opposingpower` | `FSSSignalDiscovered` | 0.65 | — |
| `option` | `Resurrect` | 0.65 | — |
| `orbitalinclination` | `ScanBaryCentre` | 0.75 | `ScanBody`, `ScanOther`, `ScanPlanet` *(+1 more)* |
| `orbitalperiod` | `ScanBaryCentre` | 0.75 | `ScanBody`, `ScanOther`, `ScanPlanet` *(+1 more)* |
| `others` | `WingJoin` | 0.65 | — |
| `outerrad` | `Ring` | 0.70 | — |
| `override` | `EngineerApply` | 0.73 | — |
| `ownerid` | `BackpackItem` | 0.73 | `ChangedBackpackItem`, `CollectItems`, `DropItems` *(+1 more)* |
| `package` | `NewCommander` | 0.65 | — |
| `packtheme` | `CarrierModulePackBase` | 0.65 | `CarrierModulePackBuy`, `CarrierModulePackSell`, `CarrierShipPackBase` *(+3 more)* |
| `packtier` | `CarrierModulePackBase` | 0.70 | `CarrierModulePackBuy`, `CarrierModulePackSell`, `CarrierShipPackBase` *(+3 more)* |
| `paid` | `MaterialTrade` | 0.78 | — |
| `parents` | `ScanBody` | 0.75 | `ScanOther`, `ScanPlanet`, `ScanStar` |
| `part` | `Continued` | 0.70 | `Fileheader` |
| `passengercount` | `MissionAccepted` | 0.70 | — |
| `passengermission` | `Mission` | 0.61 | — |
| `passengers` | `Statistics` | 0.61 | — |
| `passengertype` | `MissionAccepted` | 0.65 | — |
| `passengervips` | `MissionAccepted` | 0.61 | — |
| `passengerwanted` | `MissionAccepted` | 0.61 | — |
| `payeefaction` | `DatalinkVoucher` | 0.65 | — |
| `payment` | `ColonisationConstructionResource` | 0.70 | — |
| `pendingdecommission` | `CarrierStats` | 0.61 | — |
| `periapsis` | `ScanBaryCentre` | 0.75 | `ScanBody`, `ScanOther`, `ScanPlanet` *(+1 more)* |
| `permitsawarded` | `MissionCompleted` | 0.65 | — |
| `pilotname` | `Bounty` | 0.65 | `ShipTargeted` |
| `pilotname_localised` | `Bounty` | 0.65 | `ShipTargeted` |
| `pilotrank` | `ShipTargeted` | 0.55 | — |
| `planetclass` | `ScanOther` | 0.66 | `ScanPlanet`, `ScanStar` |
| `planetradius` | `Status` | 0.80 | — |
| `playerbalance` | `CarrierBankTransfer` | 0.70 | — |
| `playercontrolled` | `Liftoff` | 0.66 | `Touchdown`, `LaunchFighter`, `LaunchSRV` |
| `playerpilot` | `HullDamage` | 0.61 | — |
| `power` | `Interdicted` | 0.65 | `Interdiction`, `Powerplay`, `PowerplayCollect` *(+10 more)* |
| `powerplayconflictprogress` | `FSDJump` | 0.66 | `CarrierJump`, `Location` |
| `powerplayorigin` | `EjectCargo` | 0.69 | — |
| `powerplaystate` | `FSDJump` | 0.66 | `CarrierJump`, `Location` |
| `powerplaystatecontrolprogress` | `FSDJump` | 0.75 | `CarrierJump`, `Location` |
| `powerplaystatereinforcement` | `FSDJump` | 0.75 | `CarrierJump`, `Location` |
| `powerplaystateundermining` | `FSDJump` | 0.75 | `CarrierJump`, `Location` |
| `powers` | `FSDJump` | 0.69 | `CarrierJump`, `Location` |
| `price` | `CarrierTradeOrder` | 0.75 | `BuySuit`, `BuyWeapon`, `CarrierBuy` *(+5 more)* |
| `pricelist` | `ExtendedShipyard` | 0.61 | — |
| `probesused` | `SAAScanComplete` | 0.75 | — |
| `progress` | `CargoDepot` | 0.75 | `FSSDiscoveryScan`, `EngineerBase`, `LockedEngineer` *(+1 more)* |
| `providedamount` | `ColonisationConstructionResource` | 0.73 | — |
| `purchaseorder` | `CarrierTradeOrder` | 0.75 | — |
| `quality` | `EngineerCraft` | 0.70 | `EngineerLegacyConvert`, `ModuleRetrieve`, `ModuleStore` |
| `quantity` | `EngineerContribution` | 0.70 | — |
| `radius` | `ScanPlanet` | 0.75 | `ScanStar` |
| `rank` | `Powerplay` | 0.70 | `PowerplayRank`, `UnlockedEngineer` |
| `rankcombat` | `NpcCrewRank` | 0.61 | — |
| `rankprogress` | `UnlockedEngineer` | 0.70 | — |
| `raw` | `Materials` | 0.61 | — |
| `reason` | `DockingDenied` | 0.69 | — |
| `received` | `TradeMicroResources` | 0.69 | `MaterialTrade` |
| `received_localised` | `TradeMicroResources` | 0.69 | — |
| `refund` | `CancelDropship` | 0.70 | `CancelTaxi`, `CarrierModulePackSell`, `CarrierShipPackSell` |
| `region` | `CodexEntry` | 0.65 | — |
| `region_localised` | `CodexEntry` | 0.65 | — |
| `remaining` | `ProspectedAsteroid` | 0.70 | — |
| `remainingjumpsinroute` | `FSDTarget` | 0.60 | — |
| `removed` | `BackpackChange` | 0.61 | — |
| `replacementitem` | `ModuleStore` | 0.65 | — |
| `reputation` | `MissionAccepted` | 0.65 | — |
| `requiredamount` | `ColonisationConstructionResource` | 0.70 | — |
| `reservebalance` | `CarrierFinance` | 0.70 | — |
| `reservelevel` | `ScanPlanet` | 0.66 | — |
| `reservepercent` | `CarrierFinance` | 0.70 | — |
| `resources` | `UpgradeSuit` | 0.61 | `UpgradeWeapon` |
| `resourcesrequired` | `ColonisationConstructionDepot` | 0.65 | — |
| `retreat` | `BookDropship` | 0.61 | `BookTaxi` |
| `retrieveditem` | `ModuleRetrieve` | 0.65 | — |
| `retrieveditem_localised` | `ModuleRetrieve` | 0.65 | — |
| `reward` | `Bounty` | 0.70 | `CapShipBond`, `CommunityGoalReward`, `DatalinkVoucher` *(+4 more)* |
| `rewards` | `Bounty` | 0.61 | — |
| `ringclass` | `Ring` | 0.61 | — |
| `rings` | `ScanBody` | 0.66 | `ScanOther`, `ScanPlanet`, `ScanStar` |
| `role` | `ChangeCrewRole` | 0.65 | `CrewAssign`, `CrewMemberRoleChange` |
| `rotationperiod` | `ScanPlanet` | 0.75 | `ScanStar` |
| `route` | `ExtendedNavRoute` | 0.61 | — |
| `saleorder` | `CarrierTradeOrder` | 0.75 | — |
| `scanstage` | `ShipTargeted` | 0.60 | — |
| `scantype` | `ScanOrganic` | 0.69 | `Scanned`, `ScanBody`, `ScanOther` *(+2 more)* |
| `scooped` | `FuelScoop` | 0.70 | — |
| `search_and_rescue` | `Statistics` | 0.61 | — |
| `security_localised` | `Docked` | 0.69 | — |
| `selectedweapon` | `Status` | 0.73 | — |
| `selectedweapon_localised` | `Status` | 0.73 | — |
| `sellitem` | `ModuleBuy` | 0.65 | `ModuleSell`, `ModuleSellRemote` |
| `sellitem_localised` | `ModuleBuy` | 0.65 | `ModuleSell`, `ModuleSellRemote` |
| `selloldship` | `ShipyardBuy` | 0.65 | `ShipyardSwap` |
| `sellprice` | `MarketSell` | 0.70 | `ModuleBuy`, `ModuleSell`, `ModuleSellRemote` *(+2 more)* |
| `sellshipid` | `SellShipOnRebuy` | 0.73 | `ShipyardBuy`, `ShipyardSell`, `ShipyardSwap` |
| `semimajoraxis` | `ScanBaryCentre` | 0.75 | `ScanBody`, `ScanOther`, `ScanPlanet` *(+1 more)* |
| `sent` | `SendText` | 0.66 | — |
| `serverid` | `FetchRemoteModule` | 0.73 | `ModuleSellRemote` |
| `sharedwithothers` | `Bounty` | 0.70 | — |
| `shieldhealth` | `ShipTargeted` | 0.60 | — |
| `shieldsup` | `ShieldState` | 0.61 | — |
| `ship_localised` | `LoadGame` | 0.65 | `ShipTargeted` |
| `shipmarketid` | `ShipyardSell` | 0.73 | `ShipyardTransfer` |
| `shippacks` | `CarrierStats` | 0.61 | — |
| `shipprice` | `SellShipOnRebuy` | 0.70 | `ShipyardBuy`, `ShipyardSell` |
| `shipshere` | `StoredShips` | 0.61 | — |
| `shipsremote` | `StoredShips` | 0.61 | — |
| `shiptype_localised` | `ShipRedeemed` | 0.65 | `ShipyardBankDeposit`, `ShipyardBuy`, `ShipyardNew` *(+4 more)* |
| `signalname` | `FSSSignalDiscovered` | 0.65 | — |
| `signalname_localised` | `FSSSignalDiscovered` | 0.65 | — |
| `signals` | `FSSBodySignals` | 0.61 | `SAASignalsFound` |
| `signaltype` | `FSSSignalDiscovered` | 0.61 | — |
| `slot` | `EngineerCraft` | 0.65 | `EngineerLegacyConvert`, `ModuleBuy`, `ModuleRetrieve` *(+2 more)* |
| `slotname` | `LoadoutEquipModule` | 0.65 | — |
| `smuggling` | `Statistics` | 0.61 | — |
| `soldier` | `Progress` | 0.70 | `Promotion`, `Rank` |
| `spaceusage` | `CarrierStats` | 0.61 | — |
| `spawningfaction` | `FSSSignalDiscovered` | 0.65 | — |
| `spawningfaction_localised` | `FSSSignalDiscovered` | 0.65 | — |
| `spawningpower` | `FSSSignalDiscovered` | 0.65 | — |
| `spawningstate` | `FSSSignalDiscovered` | 0.65 | — |
| `spawningstate_localised` | `FSSSignalDiscovered` | 0.65 | — |
| `species` | `ScanOrganic` | 0.69 | — |
| `species_localised` | `ScanOrganic` | 0.69 | — |
| `squadron` | `Statistics` | 0.61 | — |
| `squadronid` | `JoinedSquadron` | 0.73 | `LeftSquadron`, `SharedBookmarkToSquadron`, `SquadronCreated` *(+4 more)* |
| `squadronname` | `AppliedToSquadron` | 0.65 | `InvitedToSquadron`, `JoinedSquadron`, `LeftSquadron` *(+5 more)* |
| `srv` | `Disembark` | 0.61 | `Embark` |
| `srvtype` | `DockSRV` | 0.69 | `LaunchSRV`, `SRVDestroyed` |
| `srvtype_localised` | `DockSRV` | 0.69 | `LaunchSRV`, `SRVDestroyed` |
| `starclass` | `StartJump` | 0.56 | `FSDTarget` |
| `startdead` | `LoadGame` | 0.61 | — |
| `startlanded` | `LoadGame` | 0.61 | — |
| `startmarketid` | `CargoDepot` | 0.78 | — |
| `startype` | `ScanOther` | 0.66 | `ScanPlanet`, `ScanStar` |
| `station_allegiance` | `Docked` | 0.69 | `ApproachSettlement`, `Location` |
| `station_economy` | `Docked` | 0.69 | `ApproachSettlement`, `CarrierJump`, `Location` |
| `station_government` | `Docked` | 0.69 | `ApproachSettlement`, `CarrierJump`, `Location` |
| `stationeconomies` | `Docked` | 0.66 | `ApproachSettlement`, `CarrierJump`, `Location` |
| `stationeconomy_localised` | `Docked` | 0.69 | `ApproachSettlement`, `CarrierJump`, `Location` |
| `stationfaction` | `Docked` | 0.66 | `ApproachSettlement`, `CarrierJump`, `Location` |
| `stationgovernment_localised` | `Docked` | 0.69 | `ApproachSettlement`, `CarrierJump`, `Location` |
| `stationservices` | `Docked` | 0.66 | `ApproachSettlement`, `CarrierJump`, `Location` |
| `stationstate` | `Docked` | 0.69 | — |
| `status` | `Friends` | 0.65 | — |
| `stellarmass` | `ScanStar` | 0.75 | — |
| `stolen` | `CollectCargo` | 0.66 | `CollectItems` |
| `stolengoods` | `MarketSell` | 0.61 | — |
| `storageslot` | `FetchRemoteModule` | 0.70 | `ModuleSellRemote` |
| `storeditem` | `FetchRemoteModule` | 0.65 | `ModuleBuy`, `ModuleStore` |
| `storeditem_localised` | `FetchRemoteModule` | 0.65 | `ModuleBuy`, `ModuleStore` |
| `storeoldship` | `ShipyardBuy` | 0.65 | `ShipyardSwap` |
| `storeshipid` | `ShipyardBuy` | 0.73 | `ShipyardSwap` |
| `subcategory` | `CodexEntry` | 0.65 | — |
| `subcategory_localised` | `CodexEntry` | 0.65 | — |
| `subclass` | `ScanStar` | 0.75 | — |
| `submitted` | `Interdicted` | 0.61 | — |
| `subsystem` | `ShipTargeted` | 0.55 | — |
| `subsystem_localised` | `ShipTargeted` | 0.55 | — |
| `subsystemhealth` | `ShipTargeted` | 0.60 | — |
| `success` | `Interdiction` | 0.61 | — |
| `suitid` | `BuySuit` | 0.73 | `CreateSuitLoadout`, `DeleteSuitLoadout`, `LoadoutEquipModule` *(+5 more)* |
| `suitmods` | `BuySuit` | 0.65 | `CreateSuitLoadout`, `SellSuit`, `SuitLoadout` *(+1 more)* |
| `suitmoduleid` | `BuyWeapon` | 0.73 | `LoadoutEquipModule`, `SellWeapon`, `UpgradeWeapon` |
| `suitname` | `CreateSuitLoadout` | 0.65 | `DeleteSuitLoadout`, `LoadoutEquipModule`, `RenameSuitLoadout` *(+2 more)* |
| `suitname_localised` | `CreateSuitLoadout` | 0.65 | `DeleteSuitLoadout`, `LoadoutEquipModule`, `RenameSuitLoadout` *(+2 more)* |
| `surfacegravity` | `ScanPlanet` | 0.75 | — |
| `surfacepressure` | `ScanPlanet` | 0.75 | — |
| `surfacetemperature` | `ScanPlanet` | 0.75 | `ScanStar` |
| `swapoutitem` | `ModuleRetrieve` | 0.65 | — |
| `swapoutitem_localised` | `ModuleRetrieve` | 0.65 | — |
| `system` | `BuyTradeData` | 0.69 | `BuyExplorationData`, `CodexEntry`, `CommunityGoalDiscard` *(+7 more)* |
| `systemeconomy_localised` | `FSDJump` | 0.69 | `CarrierJump`, `Location` |
| `systemfaction` | `FSDJump` | 0.66 | `CarrierJump`, `Location` |
| `systemgovernment_localised` | `FSDJump` | 0.69 | `CarrierJump`, `Location` |
| `systemname` | `FSSDiscoveryScan` | 0.69 | `FSSAllBodiesFound`, `CarrierJumpRequest` |
| `systems` | `PowerplayVoucher` | 0.65 | `SellExplorationData` |
| `systemsecondeconomy` | `FSDJump` | 0.69 | `CarrierJump`, `Location` |
| `systemsecondeconomy_localised` | `FSDJump` | 0.69 | `CarrierJump`, `Location` |
| `systemsecurity_localised` | `FSDJump` | 0.69 | `CarrierJump`, `Location` |
| `target` | `Bounty` | 0.65 | `MissionAccepted`, `MissionCompleted`, `UnderAttack` |
| `target_localised` | `Bounty` | 0.65 | `MissionAccepted`, `MissionCompleted` |
| `targetfaction` | `MissionAccepted` | 0.65 | `MissionCompleted` |
| `targetlocked` | `ShipTargeted` | 0.52 | — |
| `targettype` | `MissionAccepted` | 0.65 | `MissionCompleted` |
| `targettype_localised` | `MissionAccepted` | 0.65 | `MissionCompleted` |
| `taxi` | `Docked` | 0.66 | `FSDJump`, `Liftoff`, `SupercruiseEntry` *(+8 more)* |
| `taxrate` | `CarrierFinance` | 0.70 | — |
| `taxrate_outfitting` | `CarrierFinance` | 0.70 | — |
| `taxrate_pioneersupplies` | `CarrierFinance` | 0.70 | — |
| `taxrate_rearm` | `CarrierFinance` | 0.70 | — |
| `taxrate_refuel` | `CarrierFinance` | 0.70 | — |
| `taxrate_repair` | `CarrierFinance` | 0.70 | — |
| `taxrate_shipyard` | `CarrierFinance` | 0.70 | — |
| `telepresence` | `CrewMemberJoins` | 0.61 | `CrewMemberQuits`, `CrewMemberRoleChange`, `EndCrewSession` |
| `terraformstate` | `ScanPlanet` | 0.69 | — |
| `tg_encounters` | `Statistics` | 0.61 | — |
| `thargoidwar` | `FSDJump` | 0.78 | `Location` |
| `threat` | `SupercruiseDestinationDrop` | 0.70 | — |
| `threatlevel` | `FSSSignalDiscovered` | 0.70 | — |
| `tidallock` | `ScanPlanet` | 0.78 | — |
| `timepledged` | `Powerplay` | 0.70 | — |
| `timeremaining` | `FSSSignalDiscovered` | 0.70 | — |
| `timestamp` | `Status` | 0.91 | `ApproachBody`, `BuyTradeData`, `Cargo` *(+282 more)* |
| `to` | `SendText` | 0.69 | `VehicleSwitch` |
| `to_localised` | `SendText` | 0.69 | — |
| `toitem` | `ModuleSwap` | 0.65 | — |
| `toitem_localised` | `ModuleSwap` | 0.65 | — |
| `topower` | `PowerplayDefect` | 0.65 | — |
| `toslot` | `ModuleSwap` | 0.65 | — |
| `total` | `CarrierDepositFuel` | 0.70 | `FuelScoop` |
| `totalcost` | `BuyDrones` | 0.70 | `MarketBuy` |
| `totalcount` | `TradeMicroResources` | 0.75 | `DeliverPowerMicroResources`, `NewBuyMicroResources`, `SellMicroResources` |
| `totalearnings` | `MultiSellExplorationData` | 0.70 | `SellExplorationData` |
| `totalitemstodeliver` | `CargoDepot` | 0.75 | — |
| `totalmerits` | `PowerplayMerits` | 0.70 | — |
| `totalquantity` | `EngineerContribution` | 0.70 | — |
| `totalreward` | `Bounty` | 0.70 | — |
| `totalsale` | `MarketSell` | 0.70 | `SellDrones` |
| `trade` | `Progress` | 0.70 | `Promotion`, `Rank` |
| `tradertype` | `MaterialTrade` | 0.69 | — |
| `trading` | `Statistics` | 0.61 | — |
| `traits` | `CodexEntry` | 0.65 | — |
| `transfercost` | `FetchRemoteModule` | 0.70 | — |
| `transferprice` | `ShipyardTransfer` | 0.70 | — |
| `transfers` | `CargoTransfer` | 0.66 | `TransferMicroResources` |
| `transfertime` | `FetchRemoteModule` | 0.70 | `ShipyardTransfer` |
| `type` | `CollectCargo` | 0.69 | `DataScanned`, `EjectCargo`, `BuyDrones` *(+15 more)* |
| `type_localised` | `CollectCargo` | 0.69 | `DataScanned`, `EjectCargo`, `MarketBuy` *(+6 more)* |
| `unladenmass` | `Loadout` | 0.70 | — |
| `updatetype` | `CargoDepot` | 0.69 | — |
| `usershipid` | `SetUserShipName` | 0.73 | — |
| `usershipname` | `SetUserShipName` | 0.65 | — |
| `ussthreat` | `USSDrop` | 0.70 | — |
| `usstype` | `FSSSignalDiscovered` | 0.65 | `USSDrop` |
| `usstype_localised` | `FSSSignalDiscovered` | 0.65 | `USSDrop` |
| `variant` | `ScanOrganic` | 0.69 | `CarrierBuy` |
| `variant_localised` | `ScanOrganic` | 0.69 | — |
| `vessel` | `Cargo` | 0.66 | — |
| `victim` | `CommitCrime` | 0.65 | `PVPKill` |
| `victim_localised` | `CommitCrime` | 0.65 | — |
| `victimfaction` | `Bounty` | 0.65 | `CapShipBond`, `DatalinkVoucher`, `FactionKillBond` |
| `victimfaction_localised` | `Bounty` | 0.65 | `CapShipBond`, `FactionKillBond` |
| `volcanism` | `ScanPlanet` | 0.69 | — |
| `votes` | `Powerplay` | 0.70 | `PowerplayVote` |
| `voucheramount` | `CodexEntry` | 0.70 | — |
| `wanted` | `Docked` | 0.66 | `FSDJump`, `Location` |
| `wasdiscovered` | `ScanBody` | 0.66 | `ScanOther`, `ScanPlanet`, `ScanStar` |
| `wasfootfalled` | `ScanBody` | 0.66 | `ScanOther`, `ScanPlanet`, `ScanStar` |
| `waslogged` | `ScanOrganic` | 0.66 | — |
| `wasmapped` | `ScanBody` | 0.66 | `ScanOther`, `ScanPlanet`, `ScanStar` |
| `weaponmods` | `BuyWeapon` | 0.65 | `LoadoutEquipModule`, `SellWeapon` |
| `width` | `Screenshot` | 0.73 | — |
| `wing` | `MissionAccepted` | 0.61 | — |
| `withdraw` | `CarrierBankTransfer` | 0.70 | — |

---
