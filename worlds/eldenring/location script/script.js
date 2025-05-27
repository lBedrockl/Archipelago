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
            if(!split[0].includes('Unique location') && !split[0].startsWith("By ") && !split[0].startsWith("Shop ")){
                var itemInfo = [
                    split[0], // item
                    key.Key, // key
                    [], // tags
                    '' // desc
                ]
                if(key.Tags != `` && key.Tags != 'aaaaaaaaaaaaaaaaa') itemInfo[2] = key.Tags.split(' ')
                if(key.Text && key.Text != "aaaaaaaaaaaaaaaaa") itemInfo[3] = key.Text
                //shop tag
                if(split[1] && split[1].includes('shop')) {
                    if(!itemInfo[2]) itemInfo[2] = []
                    itemInfo[2].push('shop')
                }

                // multiples
                if(split[split.length -1].includes("x") && !isNaN(split[split.length -1].at(split[split.length -1].lastIndexOf("x") - 1))){
                    if(!multList[split[0]]) multList[split[0]] = []
                    if(split[split.length -1].at(split[split.length -1].lastIndexOf("x") - 2) != " "){
                        itemInfo[0] += ' x' + split[split.length -1].slice(split[split.length -1].lastIndexOf("x") -2, split[split.length -1].lastIndexOf("x"))
                        if(!multList[split[0]].includes(' x' + split[split.length -1].slice(split[split.length -1].lastIndexOf("x") -2, split[split.length -1].lastIndexOf("x")))){
                            multList[split[0]].push(' x' + split[split.length -1].slice(split[split.length -1].lastIndexOf("x") -2, split[split.length -1].lastIndexOf("x")))
                        }
                    }else{
                        itemInfo[0] += ' x' + split[split.length -1].slice(split[split.length -1].lastIndexOf("x") -1, split[split.length -1].lastIndexOf("x"))
                        if(!multList[split[0]].includes(' x' + split[split.length -1].slice(split[split.length -1].lastIndexOf("x") -1, split[split.length -1].lastIndexOf("x")))){
                            multList[split[0]].push(' x' + split[split.length -1].slice(split[split.length -1].lastIndexOf("x") -1, split[split.length -1].lastIndexOf("x")))
                        }
                    }
                }
                itemList[key.Area].push(itemInfo)
            }
        })
    });
    // for items
    Object.keys(itemList).forEach(area => {
        if(area != 'unknown'){
            output += `"${area}":[\n`
            itemList[area].forEach(item => {
                output += `    ERLocationData("/: ${item[0]} - ${item[3]}", "${item[0]}", key="${item[1]}"` //start
                if(item[2]) item[2].forEach(tag => { if(tag != "exclude:chrysalidsmemento") output += `, ${tag}=True`}) //tags
                output+="),\n" //cap off
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



