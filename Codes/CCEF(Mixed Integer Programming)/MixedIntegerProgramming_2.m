r = csvread('p1.csv');
Q = csvread('port1_cv.csv');
N = length(r);

xvars = 1:N;
vvars = N+1:2*N;
zvar = 2*N+1;

lb = zeros(2*N+1,1);
ub = ones(2*N+1,1);
ub(zvar) = Inf;

M = 10;
m = 10;
A = zeros(1,2*N+1); % Allocate A matrix
A(vvars) = 1; % A*x represents the sum of the v(i)
A = [A;-A];
b = zeros(2,1); % Allocate b vector
b(1) = M;
b(2) = -m;

fmin = 0.01;
fmax = 1;

Atemp = eye(N); % Identity mat of dim N X N
Amax = horzcat(Atemp,-Atemp*fmax,zeros(N,1));
A = [A;Amax];
b = [b;zeros(N,1)];
Amin = horzcat(-Atemp,Atemp*fmin,zeros(N,1));
A = [A;Amin];
b = [b;zeros(N,1)];

Aeq = zeros(1,2*N+1); % Allocate Aeq matrix
Aeq(xvars) = 1;
beq = 1;

stored = [];

for i = 0:2000,
    if mod(i,100)==0,
        fprintf('%d ',i/100);
    end
    lambda = i/2000;
    f = [-(1-lambda)*r;zeros(N,1);lambda];

    options = optimoptions(@intlinprog,'Display','off'); % Suppress iterative display
    [xLinInt,fval,exitFlagInt,output] = intlinprog(f,vvars,A,b,Aeq,beq,lb,ub,options);

    thediff = 1e-4;
    iter = 1; % iteration counter
    assets = xLinInt(xvars); % the x variables
    truequadratic = assets'*Q*assets;
    zslack = xLinInt(zvar); % slack variable value

    %history = [truequadratic,zslack];

    while abs((zslack - truequadratic)/truequadratic) > thediff % relative error
        newArow = horzcat(2*assets'*Q,zeros(1,N),-1); % Linearized constraint
        A = [A;newArow];
        b = [b;truequadratic];
        % Solve the problem with the new constraints
        [xLinInt,fval,exitFlagInt,output] = intlinprog(f,vvars,A,b,Aeq,beq,lb,ub,options);
        assets = (assets+xLinInt(xvars))/2; % Midway from the previous to the current
        % assets = xLinInt(xvars); % Use the previous line or this one
        truequadratic = assets'*Q*assets;
        zslack = xLinInt(zvar);
        % history = [history;truequadratic,zslack];
        iter = iter + 1;
    end
    ret = r'*xLinInt(xvars);
    ris = xLinInt(xvars)'*Q*xLinInt(xvars);
    obj = lambda*ris - (1-lambda)*ret;
    solution = [ xLinInt(xvars); ret ; ris; obj ];
    
    if (i==0)
        dlmwrite('final_stored_1.csv',[solution], ',');
    else
        OldData = dlmread('final_stored_1.csv', ',');
        dlmwrite('final_stored_1.csv',[OldData,solution], ',');
    end
    
        
        
    
%     stored = [ stored solution];
    

end



% csvwrite('stored_2.csv',stored);
fprintf('end\n');
% figure(1);
% plot(history)
% legend('Quadratic','Slack')
% xlabel('Iteration number')
% title('Quadratic and linear approximation (slack)')
% figure(2);
% disp(output.absolutegap)
% 
% bar(xLinInt(xvars))
% grid on
% xlabel('Asset index')
% ylabel('Proportion of investment')
% title('Optimal asset allocation')

% sum(xLinInt(vvars))
% fprintf('The expected return is %g, and the risk-adjusted return is %g.\n',...
%     r'*xLinInt(xvars),-fval)
