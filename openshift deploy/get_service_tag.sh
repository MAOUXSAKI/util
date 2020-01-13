function deploy() {
    image=`oc get statefulset/$1 -o template --template '{{.metadata.name}} {{range .spec.template.spec.containers}} {{.image}}{{end}}' | awk '{print $2}'`
    repository="10.32.233.112/ami/$1"

    echo old $image
    echo new $repository:$2
    oc scale --replicas=1 statefulset $1
    if [[ "$repository:$2" != $image ]]; then
        oc set image statefulset/$1 $1=$repository:$2
        oc delete pod $1-0 --force=true --grace-period=0

    fi
}

function service_list() {
    oc get statefulset -o template --template '{{range .items}}{{.metadata.name}} {{range .spec.template.spec.containers}} {{.image}}{{end}} {{"\n"}}{{end}}' | awk '{split($2,a,":");print $1"     \t"a[2];}' > $1/service_list
}

oc login -u dev -p dev https://master.kaifa.develop:8443
oc project $2

export -f deploy







if [ "$1" == "list" ];then
    service_list $2
elif [[ "$1" == "deploy" ]]; then
    cat $2/service_list | awk 'gsub("\r","",$2);cmd="deploy "$1" "$2;system(cmd)'
fi