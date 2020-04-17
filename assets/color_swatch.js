style_dict = {'Plotly3' : ['#0508b8', '#1910d8', '#3c19f0', '#6b1cfb', '#981cfd', '#bf1cfd', '#dd2bfd', '#f246fe', '#fc67fd', '#fe88fc', '#fea5fd', '#febefe', '#fec3fe'],
'algae' : ['#d6f9cf', '#bae4ae', '#9cd18f', '#7cbf73', '#55ae5b', '#259d51', '#078a4e', '#0d7547', '#175f3d', '#194b31', '#173723', '#112414'],
'amp' : ['#f1ecec', '#e6d1cb', '#ddb6aa', '#d59c89', '#cd8167', '#c46649', '#ba4a2f', '#ac2c24', '#951327', '#780e28', '#590d1f', '#3c0911'],
'deep' : ['#fdfdcc', '#ceecb3', '#9cdba5', '#6fc9a3', '#56b1a3', '#4c99a0', '#44829b', '#3e6c96', '#3e528f', '#403c73', '#362b4d', '#271a2c'],
'dense' : ['#e6f0f0', '#bfdde5', '#9cc9e2', '#81b4e3', '#739ae4', '#757fdd', '#7864ca', '#774aaf', '#71328d', '#641f68', '#501442', '#360e24'],
'gray' : ['#000000', '#101010', '#262626', '#3b3b3b', '#515050', '#666565', '#7c7b7a', '#929291', '#ababaa', '#c5c5c3', '#e0e0df', '#fefefd'],
'haline' : ['#29186b', '#2a23a0', '#0f4799', '#125f8e', '#267489', '#358888', '#419d85', '#51b27c', '#6fc66b', '#a0d65b', '#d4e170', '#fdee99'],
'ice' : ['#030512', '#191933', '#2c2a57', '#3a3c7d', '#3e53a0', '#3e6db2', '#4886bb', '#599fc4', '#72b8cd', '#95cfd8', '#c0e5e8', '#eafcfd'],
'matter' : ['#fdedb0', '#facd91', '#f6ad77', '#f08e62', '#e76d54', '#d85053', '#c3385a', '#a82860', '#8a1d63', '#6b185d', '#4c1550', '#2f0f3d'],
'solar' : ['#331317', '#4f1c21', '#6c2424', '#872f20', '#9d4219', '#ae5814', '#bc6f13', '#c78916', '#d1a420', '#d9c02c', '#dede3b', '#e0fd4a'],
'speed' : ['#fefccd', '#efe19c', '#ddc96a', '#c2b63b', '#9da715', '#749905', '#4b8a14', '#237924', '#0b642c', '#124e2b', '#193822', '#172312'],
'tempo' : ['#fef5f4', '#dee0d2', '#bdceb5', '#99bd9c', '#6ead8a', '#419d81', '#19897d', '#127475', '#195e6a', '#1c485d', '#193350', '#141d43'],
'thermal' : ['#032333', '#0d3064', '#35329b', '#5d3e99', '#7e4d8f', '#9e5987', '#c16479', '#e17161', '#f68b45', '#fbad3c', '#f6d346', '#e7fa5a'],
'turbid' : ['#e8f5ab', '#dcdb89', '#d1c16b', '#c7a853', '#ba8f42', '#aa793c', '#97673a', '#815738', '#684835', '#503b2e', '#392d25', '#221e1b']
}


// var color_dropdown = document.getElementById("color-dropdown");
//
// color_dropdown.getElementsByClassName('Select-value-label')[0].innerText
//
// color_dropdown.getElementsByClass('Select-menu-outer')
//
// color_dropdown.onclick = function() {
//     color_dropdown.getElementsByClassName('Select-value-label')[0].innerText
//     console.log('Hello');
// }
//
// var color_dropdown = document.getElementById("color-dropdown");
//
// function checkDOMChange()
// {
//     var outer_menu = color_dropdown.getElementsByClassName('Select-menu-outer');
//
//     if (outer_menu.length > 0) {
//         var check_for_swatches = document.getElementsByClassName("swatch");
//         if( check_for_swatches.length === 0){
//
//             // console.log(outer_menu);
//             var other_options = document.getElementsByClassName("VirtualizedSelectOption");
//             for (let i = 0; i < other_options.length; i++) {
//                 // get the color list
//                 color_list = style_dict[other_options[i].innerHTML];
//                 for (let j = 0; j < color_list.length; j++) {
//                     var swatch_div = document.createElement("div");
//                     swatch_div.setAttribute("class","swatch");
//                     swatch_div.style.background = color_list[j];
//                     other_options[i].appendChild(swatch_div);
//                 }
//
//             }
//         }
//     }
//     // check for any new element being inserted here,
//     // or a particular node being modified
//
//     // call the function again after 100 milliseconds
//     setTimeout( checkDOMChange, 100 );
// }
// checkDOMChange();

function docReady(fn) {
    // see if DOM is already available
    if (document.readyState === "complete" || document.readyState === "interactive") {
        // call on next available tick
        setTimeout(fn, 1);
    } else {
        document.addEventListener("DOMContentLoaded", fn);
    }
}

// docReady(function() {
//     // DOM is loaded and ready for manipulation here
// });


var dropdown_observer = new MutationObserver(function(mutations) {
    var color_dropdown = document.getElementById("color-dropdown");
    if (document.querySelector("#color-dropdown > div > div.Select-menu-outer") != null){

        if (color_dropdown.contains(document.querySelector("#color-dropdown > div > div.Select-menu-outer")) ) {
            var outer_menu = color_dropdown.getElementsByClassName('Select-menu-outer');
            if ( outer_menu != null){

                if (outer_menu.length > 0) {
                    var check_for_swatches = document.getElementsByClassName("swatch");
                    // console.log(outer_menu);
                    var other_options = document.getElementsByClassName("VirtualizedSelectOption");
                    for (let i = 0; i < other_options.length; i++) {
                        // get the color list
                        color_list = style_dict[other_options[i].innerHTML];
                        if( typeof color_list != "undefined"){
                            for (let j = 0; j < color_list.length; j++) {
                                var swatch_div = document.createElement("div");
                                swatch_div.setAttribute("class","swatch");
                                swatch_div.style.background = color_list[j];
                                other_options[i].appendChild(swatch_div);
                            }
                        }

                    }
                    // if( check_for_swatches.length === 0){
                    //
                    // }
                }
            }
            //observer.disconnect();
        }
    }
});

dropdown_observer.observe(document, {attributes: false, childList: true, characterData: false, subtree:true});

