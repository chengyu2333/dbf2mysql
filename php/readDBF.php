<?php
    
    error_reporting(0);
    date_default_timezone_set('Asia/Shanghai');

    //只执行9:30-15:00
    if(!(time_range('09:29:30','11:36:00') || time_range('12:59:00','15:31:00'))){
        return false;
    }

    $filename = 'nqhq.dbf';
    $configs['tbname'] = "ts_hq";
    $configs['_tbname'] = "ts_hq_bak";
    $configs['key'] = "HQZQDM";
    $configs['date'] = "HQZQJC";
    $configs['time'] = "HQCJBS";
    $configs['cacheKeySj'] = 1;
    $configs['type'] = 2;
    $configs['is_gl'] = 0;

    if(!file_exists($filename)) {
        echo '文件不存在';
        exit;
    }
    $fdbf = fopen($filename, 'r');
    $buf = fread($fdbf, 32);
    $header = unpack("VRecordCount/vFirstRecord/vRecordLength",substr($buf, 4, 8));
    $goon = true;
    $unpackString = '';
    // echo file_get_contents('nqhq.dbf');
    while ($goon && ! feof($fdbf)) { // read fields:
        $buf = fread($fdbf, 32);
        if (substr($buf, 0, 1) == chr(13)) {
            $goon = false;
        }else {         // end of field list
            $field = unpack(
                    "a11fieldname/A1fieldtype/Voffset/Cfieldlen/Cfielddec",
                    substr($buf, 0, 18));
            // echo 'Field: ' . json_encode($field) . '<br/>';
            $unpackString .= "A$field[fieldlen]$field[fieldname]/";

            // $unpackString .= 'A'.$field['fieldlen'].$field['fieldname'].'/';
            array_push($fields, $field);

            // dump($field);
        }
    }
    fseek($fdbf, $header['FirstRecord'] + 1); // move back to the start of the

    for ($i = 1; $i <= $header['RecordCount']; $i ++) {
        $buf = fread($fdbf, $header['RecordLength']);
        $record = unpack($unpackString, $buf);
        if(!isset($record[$configs['key']])){
            continue;
        }
        $record['HQZQJC'] = iconv('GBK','UTF-8',$record['HQZQJC']);
        if($record[$configs['key']] == '000000'){//key 为000000的 存储相关信息
            $sfm = trim($record[$configs['time']]);
            if(strlen($sfm) == 5){
                $sfm = "0".$sfm;
            }
            $tmpLasttime = date("Y-m-d H:i:s",strtotime($record[$configs['date']].$sfm));
            if($tmpLasttime != $lasttime){
                $lasttime = $tmpLasttime;
                if($configs['cacheKeySj'] == 1){
                    //缓存key的一部分
                    $cacheKeySj = date("YmdHis",strtotime($record[$configs['date']].$sfm));
                }
                file_put_contents($configs['tmpSjPath'],$lasttime);
                if($configs['is_gl'] == 1 && $tmpLasttime < date("Y-m-d").' 09:25:00'){
                    fclose($fdbf);//没有新数据,结束流程
                    exit();
                }
                if($configs['is_gl'] == 1 && $tmpLasttime >= date("Y-m-d").' 15:00:00'){
                    $lasttime = date("Y-m-d").' 15:00:00';
                }
            }else{
                fclose($fdbf);//没有新数据,结束流程
                exit();
            }
        }else{
            $vt = "";
            $code="";
            $name="";
            $price = "";
            $zuo = "";
            $max = "";
            $min = "";
            $rk = 0;
            foreach($record as $k=>$rv){//循环读取数据
                //如果时间在9：30之前，pass
                // if($tmpLasttime < strtotime(date("Y-m-d".' 09:30:00'))){
                //     exit;
                // }

                $rv = preg_replace("/ /si","",$rv);
                // $rv = iconv ('GBK','UTF-8//IGNORE', $rv);
                // $configs['tbname']($rv,$rk);//每种类型数据处理不一样
                if($i == 2){
                    if($rk-1 > 0){
                        $ct .= "`f".($rk-1)."`,";
                    }
                }
                if($rk == 0){
                    $code = $rv;
                    $_list['code'] = $code;
                    $_list['time'] = strtotime($tmpLasttime);
                }else if($rk == 1){
                    $name = $rv;
                }else{
                    $vt .= "'".$rv."',";
                }
                if ($rk == 2){
                    $zuo = $rv;
                }
                if ($rk == 4) {
                    $_list['price'] = $rv;
                    $price = $rv;
                }
                if ($rk == 5) {
                    $_list['num'] = $rv;
                }
                if ($rk == 8) {
                    $max = $rv;
                }
                if ($rk == 9) {
                    $min = $rv;
                }
                $rk++;
            }            
            if($price == 0){
                $updown = 0;
            }else{
                $updown = ($price-$zuo)/$zuo*100;
            }
            $zhenfu = ($max-$min)/$zuo*100;
            $list[] = $_list;//组装需要文件保存的数据
            unset($_list);
            $sql .= "(".$vt."'".$lasttime."','".$code."','".$name."','".$updown."','".$zhenfu."'),";
            // $cacaheObj->set($configs['tbname']."_".$code.$cacheKeySj,$vt."'".$lasttime."','".$code."','".$name,false,28800);
        }
    }
    $sql = substr($sql,0,-1);
    fclose($fdbf);

    //插入数据库
    $host = '192.168.1.243';
    $database = 'xsbcms';
    $username = 'sunny';
    $password = '%A@Sy+18^9';
    // $host = 'localhost';
    // $database = 'xsbcms';
    // $username = 'root';
    // $password = '512121855';
    $connection = mysql_connect($host, $username, $password);//连接到数据库
    mysql_query("set names 'utf8'");//编码转化
    if (!$connection) {
      die("could not connect to the database.\n" . mysql_error());//诊断连接错误
    }
    $selectedDb = mysql_select_db($database);//选择数据库
    if (!$selectedDb) {
      die("could not to the database\n" . mysql_error());
    }
    $sql2 = 'delete from '.$configs['_tbname'];
    $result2 = mysql_query($sql2);//清空数据库
    $sql = "INSERT INTO ".$configs['_tbname']."(". $ct ."`f0`,`code`,`name`,`updown`,`zhenfu`) VALUES ".$sql;
    $result = mysql_query($sql);

    //修改表名称
    mysql_query("alter table ts_hq rename ts_hq_tmp");
    mysql_query("alter table ts_hq_bak rename ts_hq");
    mysql_query("alter table ts_hq_tmp rename ts_hq_bak");

    mysql_close($connection);
    // dump($sql);
    // if($sql != ""){
    //  // dump($ct);die;
    //     $sql = "INSERT INTO ".$configs['tbname']."(". $ct ."`f0`,`code`,`name`) VALUES ".$sql;
    //     // dump($sql);die;
    //     // $sqls = "DELETE FROM ".$configs['tbname']." WHERE f0 = '".$lasttime."'";//清空上次数据
    //     // M()->query($sqls);
    //     $rt = M()->query($sql);
    // }
    // file_put_contents('11111.sql', $sql);
    $dirname = 'data/hangqing';
    if (!is_dir($dirname)) {
        mkdir($dirname);
    }
    foreach ($list as $key => &$value) {
        $hqdir = $dirname.'/'.$value['code'];
        if (!is_dir($hqdir)) {
            mkdir($hqdir);
        }//每个code一个路径
        $filename = $hqdir.'/'.$value['code'].'.php';
        $arr = $value['time'].','.$value['price'].','.$value['num'].'|';
        $file = fopen($filename, 'a');
        fwrite($file, $arr);
        fclose($file);
    }


    function time_range($beginTime, $endTime) {
        $ymd = date('Ymd',time());

        $strb = strtotime($ymd.' '.$beginTime);
        $stre = strtotime($ymd.' '.$endTime);
        $time = time();

        if (($time - $strb) > 0 && ($time - $stre) < 0) {
            return true;
        } else {
            return false;
        }
    }
?>
