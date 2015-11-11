#!/bin/bash
#Anand Pandey 12109
if [ $# -lt 3 ]; then
	echo "Underflow of arguements :"
	echo "Usage: ftpm [options] <servername> <file/pathname> <email-id>"
	exit
fi
echo -n Username:
read username 
#username="hobbit"
echo -n Password:
read -s password
#password="."
echo
USER=$username
PASS=$password
# if flag is not supplied

if [ $# == 3 ];then
	HOST=$1
	if [ -f $2 ];
		then
		l=`ftp -n $HOST <<End-Of-Session 
user $USER $PASS
put $2
bye
End-Of-Session`
		echo $l
		echo "File '$2' Uploaded to $1 " | mail -s "File uploaded" $3
		
	else
		echo "<error> File $2 does not exists"
	fi
fi
# if flag is supplied
if [ $# == 4 ];then
l=`ftp -n $2 <<End-Of-Session 
user $USER $PASS
put $3
bye
End-Of-Session`
	if [[ "$1" == "-l" ]]; then
		
		if [ -f $3 ];
		then
		echo $l	
		echo "(ftp://$2/$3)"	
		echo "File '$3' (ftp://$2/$3) Uploaded to $2 " | mail -s "File uploaded" $4
		else
			echo "<error> File $3 does not exists"
		fi
	elif [[ "$1" == "-a" ]]; then
		
		if [ -f $3 ];
		then
		echo $l		
		echo "File '$3' Uploaded to $2 " | mail --attach "$3" -s "File uploaded" $4
		else
			echo "<error> File $3 does not exists"
		fi
	elif [[ "$1" == "-s" ]]; then
		
		if [ -f $3 ];
		then
		echo $l		
		FILESIZE=$(stat -c%s "$3")
		echo "File '$3' (size=$FILESIZE bytes) Uploaded to $2 " | mail -s "File uploaded" $4
		else
			echo "<error> File $3 does not exists"
		fi
	fi	
fi

if [ $# -gt 4 ];then 

link=false
attach=false
path=false
multiple=false
zip=false
count=0
file_path=''
file_count=0
flags=0
size=false

declare -a files_array
array_index=0
email=''
for i in ${@} ; do
	flags=0
	if [[ $count -eq $(($file_count+1)) ]];then
		if [ "$path" = true ];then
			file_path=$i
			flags=1
		fi
	fi 
	if [[ "$i" == "-l" ]];then
		link=true
		flags=1
	fi
	if [[ "$i" == "-a" ]];then
		attach=true;
		flags=1
	fi
	if [[ "$i" == "-p" ]];then
		path=true
		file_count=$count
		flags=1
	fi
	if [[ "$i" == "-m" ]];then
		multiple=true
		flags=1
	fi
	if [[ "$i" == "-z" ]];then
		zip=true
		flags=1
	fi
	if [[ "$i" == "-s" ]];then
		size=true
		flags=1
	fi
	if [[ $flags -eq 0 ]];then
		if [[ $count != $(($#-1)) ]];then
			files_array[$array_index]=$i
			array_index=$(($array_index+1))	
		else
			email=$i		
		fi	
	fi
	count=$(($count+1))
done

server=${files_array[0]}
unset files_array[0]
file_count=0

file_zip_name=''
if [ "$zip" = true ];then
	echo `mkdir upload`
	for i in "${files_array[@]}"
	do
	file_count=$(($file_count+1))
    	`cp $i upload`
	done
	current_time=$(date "+%Y.%m.%d-%H.%M.%S")
	ext=".zip"
	files_name="upload_"$current_time$ext
	s=`zip -r $files_name upload`
	if [ "$path" = true ];then
   	l=`ftp -n $server <<End-Of-Session 
user $USER $PASS
cd $file_path
put $files_name
bye
End-Of-Session`
	else
	l=`ftp -n $server <<End-Of-Session 
user $USER $PASS
put $files_name
bye
End-Of-Session`
	fi
	echo $l
	file_zip_name=$files_name
	`rm -rf upload`
else
	for i in "${files_array[@]}"
	do
	file_count=$(($file_count+1))
	if [ "$path" = true ];then
   	l=`ftp -n $server <<End-Of-Session 
user $USER $PASS
cd $file_path
put $i
bye
End-Of-Session`
	else
	l=`ftp -n $server <<End-Of-Session 
user $USER $PASS
put $i
bye
End-Of-Session`
	fi
	echo $l
	done
fi
link_message=''
if [ "$link" = true ];then
	link_message=''
	if [ "$zip" = true ];then
	if [ "$path" = true ];then 
	link_message=$link_message"$file_zip_name(ftp://$server/$file_path/$file_zip_name) "
	else
	link_message=$link_message"$file_zip_name(ftp://$server/$file_zip_name) "
	fi	
	else
	for i in "${files_array[@]}"
	do
	if [ "$path" = true ];then 
	link_message=$link_message"$i(ftp://$server/$file_path/$i) "
	else
	link_message=$link_message"$i(ftp://$server/$i) "
	fi
	done
	fi
fi
attach_messgae=''
if [ "$attach" = true ];then
	if [ "$zip" = true ];then
	attach_message=$attach_message" --attach $file_zip_name "
	else
	for i in "${files_array[@]}"
	do
	attach_message=$attach_message" --attach $i "	
	done
	fi
fi
sizex=0
if [ "$size" = true ];then
	if [ "$zip" = true ];then
	sizex=$(stat -c%s "$file_zip_name")	
	else	
	for i in "${files_array[@]}"
	do
	sizex=$(stat -c%s "$i")	
	done
	fi
fi
if [ "$size" = true ];then
echo "File have been Uploaded  $link_message and size is $sizex bytes " | mail $attach_message -s "File uploaded" $email
else
echo "Files have been Uploaded  $link_message  " | mail $attach_message -s "File uploaded" $email
fi
if [ "$zip" = true ];
then
`rm -rf $files_name`
fi


fi
