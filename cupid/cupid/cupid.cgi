#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ Cupid Counter : init.cgi - 2011/07/22
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;

# 設定ファイル取込
require './init.cgi';
my %cf = &init;

# カウンタ表示
&load_count;

#-----------------------------------------------------------
#  カウンタ表示
#-----------------------------------------------------------
sub load_count {
	# 日を取得
	$ENV{TZ} = "JST-9";
	my $mday = (localtime(time))[3];

	# IPアドレスを取得
	my $addr = $ENV{REMOTE_ADDR};

	# データ読み取り
	open(DAT,"+< $cf{logfile}") or &error;
	eval "flock(DAT, 2);";
	my $data = <DAT>;

	# データ分解
	my ($day,$ip,$all,$yes,$tod);
	if ($data =~ /D\='(\d{0,2}):?([^\']*)';C\='(\d*)';Y\='(\d*)';T\='(\d*)';/) {

		$day = $1;
		$ip  = $2;
		$all = $3;
		$yes = $4;
		$tod = $5;

	} else {
		close(DAT);
		&error;
	}

	# カウントアップ
	unless ($cf{ip_chk} && $addr eq $ip) {

		# 累計アップ
		$all++;

		# 日は同じ
		if ($mday == $day) {

			$tod++;
			$data = "D='$day:$addr';C='$all';Y='$yes';T='$tod';";

		# 日が違う場合
		} else {

			$data = "D='$mday:$addr';C='$all';Y='$tod';T='0';";
		}

		# 更新
		seek(DAT, 0, 0);
		print DAT $data;
		truncate(DAT, tell(DAT));
	}

	close(DAT);

	# 桁数調整
	while (length($all) < $cf{digit}) {
		$all = '0' . $all;
	}

	# Image::Magickのとき
	if ($cf{image_pm} == 1) {
		require $cf{magick_pl};
		&magick($all, $cf{gifdir});
	}

	# GIF画像取り込み
	my @image;
	foreach ( split(//, $all) ) {
		push(@image,"$cf{gifdir}/$_.gif");
	}

	# 画像連結
	require $cf{gifcat_pl};
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);
	print &gifcat::gifcat(@image);
	exit;
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	# エラー画像
	my @err = qw{
		47 49 46 38 39 61 2d 00 0f 00 80 00 00 00 00 00 ff ff ff 2c
		00 00 00 00 2d 00 0f 00 00 02 49 8c 8f a9 cb ed 0f a3 9c 34
		81 7b 03 ce 7a 23 7c 6c 00 c4 19 5c 76 8e dd ca 96 8c 9b b6
		63 89 aa ee 22 ca 3a 3d db 6a 03 f3 74 40 ac 55 ee 11 dc f9
		42 bd 22 f0 a7 34 2d 63 4e 9c 87 c7 93 fe b2 95 ae f7 0b 0e
		8b c7 de 02	00 3b
	};

	print "Content-type: image/gif\n\n";
	foreach (@err) {
		print pack('C*', hex($_));
	}
	exit;
}

