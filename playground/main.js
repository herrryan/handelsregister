$(document).ready(function(){
    $("button").click(function(){
	  	    var snd = {senderid: "h4b2944dfea61be814911110c21ddd974" };
              var sid = "h4b2944dfea61be814911110c21ddd974";
	  	    $.ajax({
                url: "http://www.zav.ch/modules/Mitglieder/templates/suche_detail_ajax.php",
                data: snd,
                type: "POST"
            }).done(function(response) {
              $('#'+sid).after('<div id="detailcontainerall" class="columns alpha omega eight"></div>');
              $("#detailcontainerall").html(response);
            });
            return false;
	  	});
});