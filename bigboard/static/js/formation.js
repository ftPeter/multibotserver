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
                'followers': 1,
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
                'followers': 0,
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
});