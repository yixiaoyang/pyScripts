function LecturesIndex() {
  $.get("/information/lectures/list_0.txt", {},
        function (result) {
        var str = "";
        var lines = result.split('\n');
        for (var i = 0; i < 6; i ++) {
        var par = lines[i].split('\t');
        if (par[1].length > 40) par[1] = par[1].substr(0, 40) + "...";
        if (par[2].length > 25) par[2] = par[2].substr(0, 25) + "...";
        str += "<a href='/static/interface/lecture.html?id=" + par[0] + "'><div class='lecture_line'><div class='module_item'>";
        str += par[1] + "<br />";
        str += "<div class='module_author'>";
        str += "<div class='module_author_part' style='width:130pt;'>" + par[2] + "</div>";
        str += "<div class='module_date'>" + par[3].substr(5,5) + "</div>";
        str += "</div>";
        str += "</div></div></a>";
        }
        $('#module_lecture').html(str);
        }
       );
}
