var yaml = require('js-yaml'),
fs = require('fs');

var itemList = {} // Structure is "Area": [itemInfo, itemInfo]...  itemInfo = [item, key, [tag, tag]]
var multList = {}
var output = ''

fs.readFile('./itemslots.yaml', 'utf8', function (e, data) {
    var file = yaml.load(data, 'utf8');
    
    file.Slots.forEach(key => {
        if(!itemList[key.Area]) itemList[key.Area] = []
        //parsing for items
        key.DebugText.forEach(item => {
            var split = item.split(' -')
            if(key.QuestReqs && key.QuestReqs.includes('bellbearing') || split[0].startsWith("Shop ") || split[0].startsWith("By ") 
                || split[0].includes('Unique location')) return // remove filler text and bell bearings

            
            var itemInfo = [
                split[0], // item
                key.Key, // key
                [], // tags
                '' // desc
            ]
            if(key.Tags != `` && key.Tags != 'aaaaaaaaaaaaaaaaa') itemInfo[2] = key.Tags.split(' ')
            if(key.Text && key.Text != "aaaaaaaaaaaaaaaaa") itemInfo[3] = key.Text
            // shop tag
            if(split[1] && split[1].includes('shop')) {
                if(!itemInfo[2]) itemInfo[2] = []
                itemInfo[2].push('shop')
            }
            // scarab tag
            if(split[1] && split[1].includes('Small Scarab')) {
                if(!itemInfo[2]) itemInfo[2] = []
                itemInfo[2].push('scarab')
            }

            if(split[0].includes('Remembrance')) {
                if(!itemInfo[2]) itemInfo[2] = []
                itemInfo[2].push('remembrance')
            }

            // multiples
            var found = false
            split.forEach(x => {
                if(x.includes("x") && !isNaN(x.at(x.lastIndexOf("x") - 1)) && !found
                    && !itemInfo[2].includes('norandom') && key.Area != 'unknown'){ //checks for things not on the output list
                    var mult = ''
                    if(x.at(x.lastIndexOf("x") - 2) != " "){
                        mult = ' x' + x.slice(x.lastIndexOf("x") -2, x.lastIndexOf("x"))
                    }else if(x.at(x.lastIndexOf("x") - 1) != "1"){
                        mult = ' x' + x.slice(x.lastIndexOf("x") -1, x.lastIndexOf("x"))
                    }
                    if(mult != ''){ //checks all x's if they have a number to left if yes then add it to item and multlist
                        itemInfo[0] += mult
                        if(!multList[split[0]]) multList[split[0]] = []
                        if(!multList[split[0]].includes(mult)) multList[split[0]].push(mult)
                        found = true
                    }
                }
            })
            
            itemList[key.Area].push(itemInfo)
        })
    });
    // for items
    Object.keys(itemList).forEach(area => {
        if(area != 'unknown' && !area.includes('tower_inner') && area != 'graveyard' && area != 'chapel_start'){ //areas with no items
            output += `"${area}":[\n`
            itemList[area].forEach(item => {
                if(!item[2].includes('norandom')){ //removes items with norandom tag
                    output += `    #ERLocationData("` //start
                    switch(true){ // first acro
                        case area.includes("caelid"): output += 'CL'; break
                        case area.includes("dragonbarrow"): output += 'CL'; break
                        case area.includes("limgrave"): output += 'LG'; break
                        case area.includes("stormhill"): output += 'LG'; break // in LG and SV
                        case area.includes("liurnia"): output += 'LL'; break
                        case area.includes("bellum"): output += 'LL'; break // in LL
                        case area.includes("altus") && !area.includes("scadualtus"): output += 'AP'; break
                        case area.includes("peninsula"): output += 'WP'; break
                        case area.includes("roundtable"): output += 'RH'; break
                        case area.includes("stormveil"): output += 'SV'; break
                        case area.includes("chapel"): output += 'CA'; break
                        case area.includes("leyndell2"): output += 'LAC'; break // before LRC since same text
                        case area.includes("leyndell"): output += 'LRC'; break
                        case area.includes("ainsel"): output += 'AR'; break
                        case area.includes("lakeofrot"): output += 'LR'; break
                        case area.includes("nokron"): output += 'NR'; break // before SR since same text
                        case area.includes("siofra"): output += 'SR'; break
                        case area.includes("deeproot"): output += 'DD'; break
                        case area.includes("mohgwyn"): output += 'MP'; break
                        case area.includes("farumazula"): output += 'FA'; break
                        case area.includes("gelmir"): output += 'MG'; break
                        case area.includes("volcano"): output += 'VM'; break
                        case area.includes("academy"): output += 'RLA'; break
                        case area.includes("elphael"): output += 'EBH'; break
                        case area.includes("haligtree"): output += 'MH'; break
                        case area.includes("erdtree"): output += 'ET'; break
                        case area.includes("outskirts"): output += 'CO'; break
                        case area.includes("mountaintops"): output += 'MG'; break
                        case area.includes("snowfield"): output += 'CS'; break
                        case area.includes("sewer"): output += 'SSG'; break
                        case area.includes("moonlight"): output += 'MA'; break
                        case area.includes("flamepeak"): output += 'MG'; break
                        //places without area name
                        case area.includes("graveyard_grave"): output += 'LG'; break
                        case area.includes("precipice"): output += 'LL'; break
                        //dlc
                        case area.includes("gravesite"): output += 'GP'; break
                        case area.includes("scadualtus"): output += 'SA'; break
                        case area.includes("belurat"): output += 'BTS'; break
                        case area.includes("storehouse"): output += 'SK'; break
                        case area.includes("shadowkeep"): output += 'SK'; break
                        case area.includes("enirilim"): output += 'EI'; break
                        case area.includes("westrampart"): output += 'SK'; break
                        case area.includes("fissure"): output += 'SCF'; break
                        case area.includes("fingergrounds"): output += 'FRM'; break
                        case area.includes("midramanse"): output += 'A'; break
                        case area.includes("rauhbase"): output += 'RB'; break
                        case area.includes("charo"): output += 'CHG'; break
                        case area.includes("rauhruins"): output += 'RR'; break
                        case area.includes("cerulean"): output += 'CC'; break
                        case area.includes("ellac"): output += 'ER'; break
                        case area.includes("ensis"): output += 'CE'; break
                        case area.includes("abyssal"): output += 'AW'; break
                        case area.includes("jaggedpeak"): output += 'JP'; break
                        case area.includes("scaduview"): output += 'SV'; break
                        case area.includes("hinterland"): output += 'HL'; break
                        case area.includes("scadutree"): output += 'ST'; break
                    }
                    switch(true){ // second acro
                        case area.includes("murkwatercave"): output += '/(MCV)'; break
                        case area.includes("graveyard_grave"): output += '/(FHG)'; break
                        case area.includes("tombswardcatacombs"): output += '/(TCC)'; break
                        case area.includes("impalerscatacombs"): output += '/(IC)'; break
                        case area.includes("stormfootcatacombs"): output += '/(SC)'; break
                        case area.includes("roadsendcatacombs"): output += '/(REC)'; break
                        case area.includes("murkwatercatacombs"): output += '/(MCC)'; break
                        case area.includes("blackknifecatacombs"): output += '/(BKC)'; break
                        case area.includes("cliffbottomcatacombs"): output += '/(CC)'; break
                        case area.includes("wyndhamcatacombs"): output += '/(WC)'; break
                        case area.includes("altus_grave"): output += '/(SHG)'; break
                        case area.includes("gelmir_grave"): output += '/(GHG)'; break
                        case area.includes("outskirts_grave"): output += '/(AHG)'; break
                        case area.includes("stormhill_catacombs"): output += '/(DC)'; break
                        case area.includes("altus_catacombs") && !area.includes("scadualtus"): output += '/(UC)'; break
                        case area.includes("outskirts_sidetomb"): output += '/(AST)'; break
                        case area.includes("caelid_erdtreecatacombs"): output += '/(MEC)'; break
                        case area.includes("caelid_catacombs"): output += '/(CCC)'; break
                        case area.includes("caelid_wardead"): output += '/(WDC)'; break
                        case area.includes("flamepeak_grave"): output += '/(GCHG)'; break
                        case area.includes("mountaintops_catacombs"): output += '/(GMC)'; break
                        case area.includes("snowfield_catacombs"): output += '/(CSC)'; break
                        case area.includes("snowfield_hiddenpath"): output += '/(HPH)'; break
                        case area.includes("peninsula_earthborecave"): output += '/(EC)'; break
                        case area.includes("peninsula_tombswardcave"): output += '/(TCV)'; break
                        case area.includes("limgrave_grovesidecave"): output += '/(GC)'; break
                        case area.includes("liurnia_stillwatercave"): output += '/(SC)'; break
                        case area.includes("liurnia_lakesidecave"): output += '/(LCC)'; break
                        case area.includes("gelmir_seethewatercave"): output += '/(SC)'; break
                        case area.includes("gelmir_volcanocave"): output += '/(VC)'; break
                        case area.includes("dragonbarrow_cave"): output += '/(DB)'; break
                        case area.includes("dragonbarrow_selliahideaway"): output += '/(SH)'; break
                        case area.includes("snowfield_cave"): output += '/(CF)'; break
                        case area.includes("limgrave_coastalcave"): output += '/(CC)'; break
                        case area.includes("limgrave_highroadcave"): output += '/(HC)'; break
                        case area.includes("altus_grotto"): output += '/(PG)'; break
                        case area.includes("altus_sagescave"): output += '/(SG)'; break
                        case area.includes("caelid_abandonedcave"): output += '/(AC)'; break
                        case area.includes("caelid_gaolcave"): output += '/(GC)'; break
                        case area.includes("mountaintops_cave"): output += '/(SC)'; break
                        case area.includes("peninsula_tunnel"): output += '/(MT)'; break
                        case area.includes("limgrave_tunnels"): output += '/(LT)'; break
                        case area.includes("liurnia_tunnel"): output += '/(RLCT)'; break
                        case area.includes("altus_oldtunnel"): output += '/(OAT)'; break
                        case area.includes("altus_tunnel"): output += '/(AT)'; break
                        case area.includes("caelid_gaeltunnel"): output += '/(GT)'; break
                        case area.includes("caelid_selliatunnel"): output += '/(SCT)'; break
                        case area.includes("snowfield_tunnel"): output += '/(YAT)'; break
                        case area.includes("_tower"): output += '/DV'; break
                        case area.includes("liurnia_studyhall"): output += '/(CSH)'; break
                        case area.includes("outskirts_sealedtunnel"): output += '/(ST)'; break
                        case area.includes("sewer_flame"): output += '/(FFP)'; break
                        case area.includes("sewer_catacombs"): output += '/(LC)'; break
                        case area.includes("precipice"): output += '/(RSP)'; break
                        case area.includes("limgrave_dragonchurch"): output += '/(CDC)'; break
                        case area.includes("caelid_radahn"): output += '/(WD)'; break
                        case area.includes("leyndell_erdtree"): output += '/ET'; break
                        case area.includes("caelid_postradahn"): output += '/(RC)'; break
                        //dlc
                        case area.includes("storehouse"): output += '/SH'; break
                        case area.includes("westrampart"): output += '/WR'; break
                        case area.includes("midramanse"): output += '/(MM)'; break
                        case area.includes("gravesite_catacombs"): output += '/(FRC)'; break
                        case area.includes("rauhbase_catacombs"): output += '/(SRC)'; break
                        case area.includes("scadualtus_catacombs"): output += '/(DC)'; break
                        case area.includes("gravesite_gaol"): output += '/(BG)'; break
                        case area.includes("scadualtus_gaol"): output += '/(BG)'; break
                        case area.includes("charo_gaol"): output += '/(LG)'; break
                        case area.includes("gravesite_forge"): output += '/(RFLI)'; break
                        case area.includes("scadualtus_forge"): output += '/(RFSP)'; break
                        case area.includes("rauhbase_forge"): output += '/(TRF)'; break
                        case area.includes("ellac_cave"): output += '/(RC)'; break
                        case area.includes("gravesite_dragonpit"): output += '/(DP)'; break
                        case area.includes("cerulean_rhia"): output += '/FRR'; break
                        case area.includes("scadualtus_miyr"): output += '/(CMM)'; break
                        case area.includes("hinterland_dheo"): output += '/FRD'; break
                    }
                    output += `: ${item[0]} - ${item[3]}", "${item[0]}", key="${item[1]}"` //item and comment stuff
                    if(item[2]) item[2].forEach(tag => { if(tag != "exclude:chrysalidsmemento") output += `, ${tag}=True`}) //tags
                    output+="),\n" //cap off
                }
            })
            output += `],\n`
        }
    })
    fs.writeFileSync('./location output.txt', output)

    output = ''
    // for uniqueMults
    Object.keys(multList).forEach(item => {
        output += item
            multList[item].forEach(mult => {
                output += ` ${mult}`
            })
        output += '\n'
    })
    fs.writeFileSync('./unique mults.txt', output)
});



