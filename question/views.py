from django.contrib import messages
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Max, Case, When, IntegerField
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ProblemForm
from .models import Problem, UserProblem, Company, Department, Position, CompanyProblem, Tag
from datetime import datetime


@login_required
@require_POST
def update_problem_status(request, problem_id):
    """
    AJAX 接口：切换题目完成/未做状态
    接收 POST: status = 'completed' or 'not_started'
    返回 JSON: { success: True, status: 'completed' }
    """
    problem = get_object_or_404(Problem, id=problem_id)
    new_status = request.POST.get('status', 'not_started')

    user_problem, created = UserProblem.objects.get_or_create(
        user=request.user,
        problem=problem,
        defaults={'status': new_status}
    )

    # 如果不是刚创建的，就更新状态
    if not created:
        user_problem.status = new_status

    # 如果切到“完成”，更新练习时间和计数
    if new_status == 'completed':
        user_problem.last_practice = timezone.now()
        user_problem.practice_count += 1
    user_problem.save()

    return JsonResponse({
        'success': True,
        'status': user_problem.status
    })


def random_problem(request):
    # 1. 先根据 GET 参数构建同列表页相同的 queryset
    qs = Problem.objects.all()

    company = request.GET.get('company')
    if company:
        qs = qs.filter(company_id=company)

    department = request.GET.get('department')
    if department:
        qs = qs.filter(department_id=department)

    position = request.GET.get('position')
    if position:
        qs = qs.filter(position_id=position)

    search = request.GET.get('search')
    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(number__icontains=search)
        )

    # 2. 随机选一条
    problem = qs.order_by('?').first()

    if not problem:
        messages.warning(request, "没有符合条件的题目，无法随机出题。")
        # 重定向回列表页，保留参数也行
        return redirect('problem_list')

    # # 3. 跳转到题目详情页（假设你有这样的 view）
    return redirect('problem_list')


@login_required
def problem_list(request):
    """题目列表视图"""
    # 1. 读取所有筛选／排序／分页参数
    company_id = request.GET.get('company', '')
    department_id = request.GET.get('department', '')
    position_id = request.GET.get('position', '')
    difficulty = request.GET.get('difficulty', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'number')
    selected_question_tag = request.GET.get('question_tag', '')

    # 2. 准备下拉框数据
    question_tags = Tag.objects.all()

    # 3. 构造基础 QuerySet，并预取多对多，防止 N+1
    problems = (
        Problem.objects
        .all()
        .prefetch_related('tags', 'companyproblem_set')
    )

    # 4. 逐项应用筛选
    if selected_question_tag:
        problems = problems.filter(tags__id=selected_question_tag)

    if search:
        problems = problems.filter(
            Q(title__icontains=search) |
            Q(number__icontains=search)
        )

    if difficulty:
        problems = problems.filter(difficulty=difficulty)

    if company_id:
        problems = problems.filter(companies__id=company_id)

    if department_id:
        problems = problems.filter(departments__id=department_id)

    if position_id:
        problems = problems.filter(positions__id=position_id)

    # 5. 获取当前用户的题目记录，构建一个字典便于查状态
    user_problems = (
        UserProblem.objects
        .filter(user=request.user)
        .select_related('problem')
    )
    user_problem_dict = {up.problem_id: up for up in user_problems}

    # 6. 按状态筛选
    if status:
        if status == 'completed':
            completed_ids = [
                up.problem_id
                for up in user_problems
                if up.status == 'completed'
            ]
            problems = problems.filter(id__in=completed_ids)
        elif status == 'not_started':
            done_ids = [up.problem_id for up in user_problems]
            problems = problems.exclude(id__in=done_ids)

    # 7. 统计各类数据
    total_count = problems.count()
    completed_count = user_problems.filter(status='completed').count()
    easy_count = problems.filter(difficulty='easy').count()
    medium_count = problems.filter(difficulty='medium').count()
    hard_count = problems.filter(difficulty='hard').count()

    # 8. 排序逻辑
    if sort_by == 'difficulty':
        problems = problems.annotate(
            difficulty_order=Case(
                When(difficulty='easy', then=1),
                When(difficulty='medium', then=2),
                When(difficulty='hard', then=3),
                default=4,
                output_field=IntegerField(),
            )
        ).order_by('difficulty_order', 'number')

    elif sort_by == 'status':
        # Python 层面排序：已完成在前
        problems_list = list(problems)
        problems_list.sort(key=lambda p: 0 if (user_problem_dict.get(p.id) and
                                               user_problem_dict[p.id].status == 'completed') else 1)
        problems = problems_list

    elif sort_by == 'frequency':
        # 按写入的顺序排序（示例）
        problems = problems.order_by('created_at')

    elif sort_by == 'recent':
        # 按完成时间来算
        problems = problems.annotate(
            last_practice_user=Max(
                'user_records__last_practice',
                filter=Q(user_records__user=request.user)
            )
        ).order_by('-last_practice_user', 'number')

    else:  # 默认按题号
        problems = problems.order_by('number')

    # 9. distinct 防止多对多 join 重复
    # problems = problems.distinct()

    # 10. 分页
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 11. 在每个对象上挂载用户记录 & 关联统计字段
    for prob in page_obj:
        up = user_problem_dict.get(prob.id)
        prob.user_record = up
        cp = (
            CompanyProblem.objects
            .filter(problem=prob)
            .order_by('-frequency')
            .first()
        )
        if cp:
            prob.max_frequency = cp.frequency
            prob.last_asked = cp.last_asked

    # 12. 传入模板上下文
    context = {
        'problems': page_obj,
        'total_count': total_count,
        'completed_count': completed_count,
        'easy_count': easy_count,
        'medium_count': medium_count,
        'hard_count': hard_count,
        'companies': Company.objects.all(),
        'departments': Department.objects.filter(company__id=company_id) if company_id else Department.objects.none(),
        'positions': Position.objects.filter(
            department__id=department_id) if department_id else Position.objects.none(),
        'selected_company': company_id,
        'selected_department': department_id,
        'selected_position': position_id,
        'selected_difficulty': difficulty,
        'selected_status': status,
        'search_query': search,
        'sort_by': sort_by,
        'question_tags': question_tags,
        'selected_question_tag': selected_question_tag,
    }

    return render(request, 'leetcode/problem_list.html', context)


@login_required
@require_POST
def update_problem_status(request, problem_id):
    """更新题目状态"""
    problem = get_object_or_404(Problem, id=problem_id)
    status = request.POST.get('status', 'not_started')

    user_problem, created = UserProblem.objects.get_or_create(
        user=request.user,
        problem=problem
    )

    user_problem.status = status
    if status == 'completed':
        user_problem.last_practice = datetime.now()
        user_problem.practice_count += 1
    user_problem.save()

    return JsonResponse({'success': True})


@login_required
@require_POST
def update_mastery(request, problem_id):
    """更新掌握程度"""
    problem = get_object_or_404(Problem, id=problem_id)
    mastery = int(request.POST.get('mastery', 0))

    user_problem, created = UserProblem.objects.get_or_create(
        user=request.user,
        problem=problem
    )

    user_problem.mastery = mastery
    user_problem.save()

    return JsonResponse({'success': True})


@login_required
def problem_notes(request, problem_id):
    """题目笔记"""
    problem = get_object_or_404(Problem, id=problem_id)
    user_problem, created = UserProblem.objects.get_or_create(
        user=request.user,
        problem=problem
    )

    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        user_problem.notes = notes
        user_problem.save()
        return redirect('problem_list')

    return render(request, 'leetcode/add_problem.html', {
        'problem': problem,
        'user_problem': user_problem,
    })


@login_required
def add_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.save()
            form.save_m2m()

            # 获取公司名称，处理不存在时创建
            company_name = form.cleaned_data.get('company_name')
            if company_name:
                company, _ = Company.objects.get_or_create(name=company_name)
            else:
                company, _ = Company.objects.get_or_create(name="练习")  # 默认公司

            # 绑定公司和题目
            problem.companies.add(company)

            # 创建 CompanyProblem（频度默认 1）
            cp, _ = CompanyProblem.objects.get_or_create(
                company=company,
                problem=problem,
                defaults={'frequency': 1, 'last_asked': problem.created_at.date()}
            )

            # 获取部门名称
            department_name = form.cleaned_data.get('department_name')
            if department_name:
                dept, _ = Department.objects.get_or_create(name=department_name, company=company)
                # 你可以在这里进一步扩展：cp.positions.add(...)

            return redirect('problem_list')
    else:
        form = ProblemForm()

    return render(request, 'leetcode/add_problem.html', {'form': form})
