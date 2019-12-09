//for index page

/* document.getElementById('centrality_selection').addEventListener('change', function(e) {
    var centrality = document.getElementById('centrality_selection').value;
    console.log(centrality)

    xhr = new XMLHttpRequest();
    xhr.open('GET',`/update_grade_centralities?centrality=${centrality}`, true);
    xhr.onload = function(){
        Plotly.newPlot('container_for_centralities', JSON.parse(JSON.parse(this.responseText)[1]), {displayModeBar: false});
        Plotly.newPlot('centrality_table', JSON.parse(JSON.parse(this.responseText)[2]), {displayModeBar: false});
        var chart_cont = document.getElementById('container_for_centralities');
        chart_cont.on('plotly_click', function(e){
            console.log(e['points'][0]['hovertext']);
        });
        //console.log(this.responseText);
    };
    xhr.send();
});
document.getElementById('centrality_grade_selection').addEventListener('change', function() {
    var grade = document.getElementById('centrality_grade_selection').value;
    console.log(grade)

    xhr = new XMLHttpRequest();
    xhr.open('GET',`/update_grade_centralities?grade=${grade}`, true);
    xhr.onload = function(){
        Plotly.newPlot('container_for_centralities', JSON.parse(JSON.parse(this.responseText)[1]), {displayModeBar: false});
        Plotly.newPlot('centrality_table', JSON.parse(JSON.parse(this.responseText)[2]), {displayModeBar: false});
        console.log(JSON.parse(JSON.parse(this.responseText)[1]))
        var chart_cont = document.getElementById('container_for_centralities');
        chart_cont.on('plotly_click', function(e){
            console.log(e['points'][0]['hovertext']);
        });
        //console.log(this.responseText);
    };
    xhr.send();
});
 */

// create heatmap multi selector
$('#filter_p2p_by_email').select2({
    placeholder: "Выберите email",
    allowClear: true
});
$('#emails_for_heatmap').select2({
    placeholder: "Выберите email",
    allowClear: true
});

window.onload = function() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', '/heatmap/users', true);
    xhr.onload = function(){
        var names = JSON.parse(xhr.responseText);
        names.forEach(function(each){
            var node = document.createElement("option");
            var textnode = document.createTextNode(each);
            node.appendChild(textnode);
            node.value = each;
            document.getElementById("filter_p2p_by_email").appendChild(node);
            //document.getElementById("emails_for_heatmap").appendChild(node);
        })
        names.forEach(function(each){
            var node = document.createElement("option");
            var textnode = document.createTextNode(each);
            node.appendChild(textnode);
            node.value = each;
            document.getElementById("emails_for_heatmap").appendChild(node);
        })
    }
    xhr.send();
}

$('#filter_p2p_by_email').on('select2:select', function(){
    var selected = $("#filter_p2p_by_email").val()
    xhr = new XMLHttpRequest();
    xhr.open('GET',`/interactions/update?email=${selected}`, true);
    xhr.onload = function(){
        Plotly.newPlot('p2p', JSON.parse(xhr.responseText));
    }
    xhr.send();
})


//heatmap filtering
document.getElementById('submit_update_heatmap').addEventListener('click', function(e){
    e.preventDefault();
    var selected = $("#emails_for_heatmap").val()
    xhr = new XMLHttpRequest();
    xhr.open('GET',`/heatmap/update?emails=${JSON.stringify(selected)}`, true);
    xhr.onload = function(){
        Plotly.newPlot('heatmap', JSON.parse(xhr.responseText));
    }
    xhr.send();
});

// for activity page
/* 
document.getElementById('sort_activity_stats_table').addEventListener('change', function() {
    var sort_param = document.getElementById('sort_activity_stats_table').value;
    if (sort_param != 'None') {
        xhr = new XMLHttpRequest();
        xhr.open('GET',`/update_activity?sort_param=${sort_param}`, true);
        xhr.onload = function(){
            Plotly.newPlot('place_for_table', JSON.parse(this.responseText), {displayModeBar: false});
        };
        xhr.send();
    }
});
$('#filter_activity_plots_by_email').select2()
window.onload = function(e) {
    xhr = new XMLHttpRequest();
    xhr.open('GET', '/heatmap/users', true);
    xhr.onload = function(){
        var names = JSON.parse(xhr.responseText);
        names.forEach(function(each){
            var node = document.createElement("option");
            var textnode = document.createTextNode(each);
            node.appendChild(textnode);
            node.value = each;
            document.getElementById("filter_activity_plots_by_email").appendChild(node)
        })
    }
    xhr.send();
}
$("#filter_activity_plots_by_email").on('change', function(){
    var selected = $("#filter_activity_plots_by_email").val()
    xhr = new XMLHttpRequest();
    xhr.open('GET',`/update_activity?email=${JSON.stringify(selected)}`, true);
    xhr.onload = function(){
        Plotly.newPlot('activity_plots', JSON.parse(xhr.responseText));
    }
    xhr.send();
});


$("#filter_by_email").on("select2:select", function (e) { 
    var email = $(e.currentTarget).val();
    xhr = new XMLHttpRequest();
    xhr.open('GET',`/update_activity?email=${email}`, true);
    xhr.onload = function(){
        Plotly.newPlot('p2p', JSON.parse(this.responseText), {displayModeBar: false});
        //console.log(this.responseText);
    };
    xhr.send();
    });

$("#filter_by_email").select2( {
    width: 'resolve',
    placeholder: "Выберите email",
    allowClear: true
    } );

$("#filter_by_email").on("select2:select", function (e) { 
    var email = $(e.currentTarget).val();
    xhr = new XMLHttpRequest();
    xhr.open('GET',`/update_activity?email=${email}`, true);
    xhr.onload = function(){
        Plotly.newPlot('p2p', JSON.parse(this.responseText), {displayModeBar: false});
        //console.log(this.responseText);
    };
    xhr.send();
    });


$('#centrality_boxplot').on('change',function(){
    $.ajax({
        url: "/update_timelines",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('centrality_boxplot').value
        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('cent', data, {displayModeBar: false});
        }
    });
})

$('#centrality_boxplot').on('change',function(){
    $.ajax({
        url: "/update_timelines",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('centrality_boxplot').value
        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data, {displayModeBar: false});
        }
    });

    $.ajax({
        url: "/update_p2p",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('first_cat').value
        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('p2p', data, {displayModeBar: false});
        }
    });
}) */
