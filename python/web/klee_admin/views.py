from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from decorators import group_required
from forms import AdminConfigForm
from worker.worker import celery
from worker.worker_config import WorkerConfig

HUMAN_READABLE_FIELD_NAMES = {
    "timeout": "Timeout",
    "cpu_share": "CPU Share",
    "memory_limit": "Memory Limit"
}

worker_configuration = WorkerConfig()


@group_required("admin")
def index(request):
    return render(request, "klee_admin/index.html")


@group_required("admin")
def worker_config(request):
    if request.method == 'POST':
        form = AdminConfigForm(request.POST)
        if form.is_valid():
            updated = []

            for conf in form.cleaned_data:
                data = form.cleaned_data[conf]
                if data or data == 0:
                    worker_configuration.set_config(conf, data)
                    updated.append(HUMAN_READABLE_FIELD_NAMES[conf])

            if updated:
                messages.success(request, ", ".join(updated) + " updated")

            return HttpResponseRedirect(reverse('klee_admin:worker_config'))
    else:
        timeout = worker_configuration.timeout
        cpu_share = worker_configuration.cpu_share
        memory_limit = worker_configuration.memory_limit
        form = AdminConfigForm(
            initial={'cpu_share': cpu_share, 'memory_limit': memory_limit,
                     'timeout': timeout})
    return render(request, "klee_admin/worker_config.html", {'form': form})


@group_required("admin")
def worker_list(request):
    uptime_stats = celery.control.broadcast('get_uptime_stats', reply=True)
    return render(
        request,
        "klee_admin/worker_list.html",
        {
            "uptime_stats": uptime_stats
        }
    )
