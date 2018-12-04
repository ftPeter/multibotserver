$(function(){
    $("#formation").submit(function(event){
        event.preventDefault();
        formation = $(this).find("textarea").val();

        $.ajax({
            url: "actions/formation",
            type: 'post',
            dataType: 'json',
            data: {
                'input': formation,
                'action': 'followers',
            },
            success: function(data) {
                if (data.error) {
                    $(".danger").removeAttr('hidden');
                    $("#error").text(data.error.join('. '));
                    $(".success").attr('hidden', true);
                }
                else {
                    $("#leader").removeAttr('hidden');
                    $(".danger").attr('hidden', true);
                    $(".success").attr('hidden', true);
                }
            }
        });
    });

    $("#leader-path").submit(function(event){
        event.preventDefault();
        path = $(this).find("textarea").val();

        $.ajax({
            url: "actions/formation",
            type: 'post',
            dataType: 'json',
            data: {
                'input': path,
                'action': 'leader',
            },
            success: function(data) {
                if (data.error) {
                    $(".danger").removeAttr('hidden');
                    $("#error").text(data.error.join('. '));
                    $(".success").attr('hidden', true);
                }
                else {
                    $(".danger").attr('hidden', true);
                    $(".success").removeAttr('hidden');
                }
            }
        });
    });

    $("#cancel").click(function(){
        $.ajax({
            url: "actions/formation",
            type: 'post',
            dataType: 'json',
            data: {
                'action': 'cancel',
            },
            success: function(data) {
                }
        });
    });
});