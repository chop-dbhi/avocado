define('login', function() {
    $(function() {
        var submit = $('[type=submit]'),
            username = $('[name=username]'),
            password = $('[name=password]');

        function check() {
            var t = (username.val() && password.val()) ? false : true;
            submit.attr('disabled', t);
        };

        username.keyup(check);
        password.keyup(check);
    });
});