$(function(){
    $("form").submit(function(event){
        event.preventDefault();
        input = $(this).find("textarea").val();

        robotId = $(this).attr('id').split(" ")[0];
        robotName = $(this).attr('id').split(" ")[1];

        action = $("#" + robotId + "-action").val().replace(/\s/g, '').toLowerCase();
        $.ajax({
            url: robotId + '/' + action,
            type: 'post',
            dataType: 'json',
            data: {
                'input': input
            },
            success: function(data) {
                if (data.error) {
                    $(".alert").removeAttr('hidden');
                    $("#error").text(data.error);
                }
                else {
                    message = "Robot " + robotName + ": " + action + "\n" + data.result;
                    alert(message);
                }
            }
        });
    });
});

function refresh() {
    $.ajax({
        url: '/refresh',
        type: 'post',
        success: function(data) {
            if (data.error) {
                $(".alert").removeAttr('hidden');
                $("#error").text(data.error);
            }
            else {
                location.reload();
            }
        }
    });
}
