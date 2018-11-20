$(function(){
    $("form").submit(function(event){
        event.preventDefault();
        input = $(this).find("textarea").val();
        action = $("#action").val().replace(/\s/g, '').toLowerCase();

        var selectedRobots = []

        $('.robot-check').each(function(i,obj) {
            if (obj.checked) {
                selectedRobots.push(obj.value);
            }
        });

        $.ajax({
            url: "actions/broadcast",
            type: 'post',
            dataType: 'json',
            data: {
                'input': input,
                'robots': selectedRobots.join(),
                'action': action,
            },
            success: function(data) {
                $(".alert").attr('hidden', true);
                $("#result").removeAttr('hidden');
                $("#result-table").html('');
                if (Object.keys(data).length > 0) {
                    for (var obj in data) {
                        robotRow = "<tr><td class='align-middle'>" + obj + "</td>"
                        robotRow += "<td class='align-middle'>" + data[obj].result.join('</br>') + "</td>"
                        robotRow += "<td class='align-middle'>" + data[obj].error.join('</br>') + "</td><tr>"
                        $("#result-table").append(robotRow);
                    }
                }
            },
            error: function(textStatus, errorThrown) {
                $("#error").text(errorThrown);
                $(".alert").removeAttr('hidden');
                $("#result").attr('hidden', true);
            }
        });
    });
});
