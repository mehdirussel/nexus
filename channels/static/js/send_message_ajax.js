$("#send_message_button").on('submit', '#message-send-form', function (i) {
    i.preventDefault();
    $.ajax({
        type: 'POST',
        url: "{% url 'send-message-api' %}",
        data: JSON.stringify({
            channel_id: "hehe"//"{{ channel.id }}"
            //content: $("#message-content").val(),
        }),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken'),
        },
        success: function () {
            alert('the pigeon is on its way');
        },
    });
});
