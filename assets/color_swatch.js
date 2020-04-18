style_dict = {
    //'Plotly3' : ['#1910d8', '#6b1cfb', '#bf1cfd', '#f246fe', '#fe88fc', '#febefe', '#fec3fe'],
    'algae' : ['#bae4ae', '#7cbf73', '#259d51', '#0d7547', '#194b31', '#112414'],
    'amp' : ['#e6d1cb', '#d59c89', '#c46649', '#ac2c24', '#780e28', '#3c0911'],
    'deep' : ['#ceecb3', '#6fc9a3', '#4c99a0', '#3e6c96', '#403c73', '#271a2c'],
    'dense' : ['#bfdde5', '#81b4e3', '#757fdd', '#774aaf', '#641f68', '#360e24'],
    //'gray' : ['#101010', '#3b3b3b', '#666565', '#929291', '#c5c5c3', '#fefefd'],
    //'haline' : ['#2a23a0', '#125f8e', '#358888', '#51b27c', '#a0d65b', '#fdee99'],
    //'ice' : ['#191933', '#3a3c7d', '#3e6db2', '#599fc4', '#95cfd8', '#eafcfd'],
    'matter' : ['#facd91', '#f08e62', '#d85053', '#a82860', '#6b185d', '#2f0f3d'],
    //'solar' : ['#4f1c21', '#872f20', '#ae5814', '#c78916', '#d9c02c', '#e0fd4a'],
    'speed' : ['#efe19c', '#c2b63b', '#749905', '#237924', '#124e2b', '#172312'],
    'tempo' : ['#dee0d2', '#99bd9c', '#419d81', '#127475', '#1c485d', '#141d43'],
    // 'thermal' : ['#0d3064', '#5d3e99', '#9e5987', '#e17161', '#fbad3c', '#e7fa5a'],
    'turbid' : ['#dcdb89', '#c7a853', '#aa793c', '#815738', '#503b2e', '#221e1b']
}



const indicesOfInterest = [0,3,7,11];

var dropdown_observer = new MutationObserver(function(mutations) {
    var color_dropdown = document.getElementById("color-dropdown");

    if (document.querySelector("#color-dropdown > div > div.Select-menu-outer") != null){

        if (color_dropdown.contains(document.querySelector("#color-dropdown > div > div.Select-menu-outer")) ) {
            var outer_menu = color_dropdown.getElementsByClassName('Select-menu-outer');
            if ( outer_menu != null){

                if (outer_menu.length > 0) {
                    // var check_for_swatches = document.getElementsByClassName("swatch");
                    // console.log(outer_menu);
                    var max_length = 0;
                    var other_options = document.getElementsByClassName("VirtualizedSelectOption");
                    for (let i = 0; i < other_options.length; i++) {
                        // get the color list
                        color_list = style_dict[other_options[i].innerHTML];

                        // change style of Virtualized Select option to text-align center
                        // console.log(style_div);
                        // other_options[i].innerText = "";
                        // console.log(other_options[i].innerText);
                        var swatch_container = document.createElement("div");
                        swatch_container.setAttribute("class", "swatch-container");
                        // other_options[i].appendChild(swatch_container);

                        var flag = false;
                        if( typeof color_list != "undefined"){
                            for (let j = 0; j < color_list.length; j++) {
                                if ( indicesOfInterest.includes(j) ){
                                    var swatch_div = document.createElement("div");
                                    swatch_div.setAttribute("class","swatch");
                                    swatch_div.style.background = color_list[j];
                                    swatch_div.style.display = "inline-block";
                                    swatch_container.appendChild(swatch_div);
                                    // other_options[i].appendChild(swatch_div);
                                    // other_options[i].appendChild(style_div);
                                    // swatch_container.appendChild(swatch_div);
                                }

                            }
                            style_div = document.createElement("div");
                            style_div.setAttribute("class", "swatchName");
                            style_div.innerText= other_options[i].innerText;

                            if(max_length === 0){
                                max_length = style_div.innerText.length;
                            } else if (style_div.innerText.length < max_length) {
                                style_div.innerText = style_div.innerText + " ".repeat(((max_length - style_div.innerText.length) + 1))
                            }

                            other_options[i].removeChild(other_options[i].firstChild);
                            other_options[i].appendChild(swatch_container);
                            swatch_container.insertBefore(style_div, swatch_container.firstChild);
                            // other_options[i].insertBefore(style_div, other_options[i].firstChild);
                        }

                    }

                }
            }
        }
    }
});

dropdown_observer.observe(document, {attributes: false, childList: true, characterData: false, subtree:true});

