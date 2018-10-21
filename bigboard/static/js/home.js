$(function(){
    $("form").submit(function(event){
        event.preventDefault();
        input = $(this).find("textarea").val();
        robotId = $(this).attr('id');
        action = $("#" + robotId + "-action").val().replace(/\s/g, '').toLowerCase();
        $.ajax({
            url: action + '/' + robotId,
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
                    alert('success');
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
